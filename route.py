"""Grid-based initial signal routing. Wide power paths are placed in build.py."""
from collections import defaultdict
from heapq import heappop, heappush
from math import ceil, floor, hypot

STEP = .25
WIDTH = .25
CLEARANCE = .215

def grid(x):
    return round(x / STEP)

def cells(x0, y0, x1, y1):
    for x in range(ceil(x0 / STEP), floor(x1 / STEP) + 1):
        for y in range(ceil(y0 / STEP), floor(y1 / STEP) + 1):
            yield x,y

def route_board(b, k, loaded, parts, nets, track, via):
    layers = [k.F_Cu, k.In2_Cu, k.B_Cu]
    fixed = [defaultdict(set) for _ in layers]
    viaspace = [defaultdict(set) for _ in layers]
    endpoints = defaultdict(list)
    def add_pad(p, net):
        box = p.GetBoundingBox()
        x0,y0,x1,y1 = map(k.ToMM,(box.GetX(),box.GetY(),box.GetRight(),box.GetBottom()))
        for l,layer in enumerate(layers):
            if not p.IsOnLayer(layer):
                continue
            for table,gap in [(fixed[l], CLEARANCE+WIDTH/2+.028), (viaspace[l], .64)]:
                for cell in cells(x0-gap,y0-gap,x1+gap,y1+gap):
                    table[cell].add(net)
    def add_segment(l, a, z, width, net):
        ax,ay=a; bx,by=z
        vx,vy=bx-ax,by-ay
        dd=vx*vx+vy*vy
        for table,margin in [(fixed[l], CLEARANCE+WIDTH/2+.026), (viaspace[l], .64)]:
            radius=margin+width/2
            for x,y in cells(min(ax,bx)-radius,min(ay,by)-radius,
                             max(ax,bx)+radius,max(ay,by)+radius):
                px,py=x*STEP-ax,y*STEP-ay
                t=min(1,max(0,(px*vx+py*vy)/dd)) if dd else 0
                if hypot(px-t*vx,py-t*vy)<=radius: table[x,y].add(net)
    placed_vias=[]
    names = {n.GetNetCode(): name for name,n in nets.items()}
    for ref,f in loaded.items():
        for p in sorted(f.Pads(), key=lambda pad: -pad.GetSize().x * pad.GetSize().y):
            net=names.get(p.GetNetCode(),f'!{ref}.{p.GetNumber()}')
            add_pad(p,net)
            if net not in nets or not p.GetNumber() or any(ep[:2] == (ref,p.GetNumber()) for ep in endpoints[net]):
                continue
            xy=tuple(map(k.ToMM,(p.GetPosition().x,p.GetPosition().y)))
            endpoints[net].append((ref,p.GetNumber(),xy,tuple(l for l,layer in enumerate(layers) if p.IsOnLayer(layer))))
    for t in b.GetTracks():
        net=names[t.GetNetCode()]
        start=tuple(map(k.ToMM,(t.GetStart().x,t.GetStart().y)))
        end=tuple(map(k.ToMM,(t.GetEnd().x,t.GetEnd().y)))
        width=k.ToMM(t.GetWidth(k.F_Cu) if isinstance(t,k.PCB_VIA) else t.GetWidth())
        levels=range(len(layers)) if isinstance(t,k.PCB_VIA) else (layers.index(t.GetLayer()),)
        for l in levels:
            add_segment(l,start,end,width,net)

    # Bring the fine-pitch eFuse control pins out beyond the body before grid routing.
    efuse_escapes = {
        'BYPASS_OV': ('2', (83.85, 7.2625)),
        'BYPASS_ILM': ('9', (88.7, 7.2625)),
        'BYPASS_DVDT': ('7', (88.55, 8.2125)),
    }
    for net, (pin, endpoint) in efuse_escapes.items():
        ends = endpoints[net]
        index = next(j for j, item in enumerate(ends) if item[:2] == ('U5', pin))
        prior = ends[index]
        track(net, k.F_Cu, .2, prior[2], endpoint)
        add_segment(0, prior[2], endpoint, .2, net)
        ends[index] = (*prior[:2], endpoint, (0,))
    for net, pin, target, level in [('BAT_RAW','5',(84,13),0), ('EXT_5V','6',(87.4,11.5),2)]:
        ends = endpoints[net]
        index = next(j for j, item in enumerate(ends) if item[:2] == ('U5', pin))
        ends[index] = ('U5', pin, target, (level,))
    ground = next(p for p in endpoints['GND'] if p[:2] == ('U5','8'))
    ground_via = (89.3, 7.7375)
    track('GND',k.F_Cu,.2,ground[2],ground_via)
    add_segment(0,ground[2],ground_via,.2,'GND')
    via('GND',*ground_via,.55,.3)
    placed_vias.append(ground_via)
    for l in range(len(layers)):
        add_segment(l,ground_via,ground_via,.55,'GND')

    # Dedicated staggered through-vias escape the QFN into the inner routing layer.
    for n,ends in endpoints.items():
        for j,ep in enumerate(ends):
            if ep[0]!='U4' or ep[1]=='17': continue
            x,y=ep[2]; dx=x-46;dy=y-33.3
            length=1.05 if int(ep[1])%2 else 1.68
            if abs(dx)>abs(dy): end=(x+(length if dx>0 else -length),y)
            else: end=(x,y+(length if dy>0 else -length))
            track(n,k.F_Cu,.20,(x,y),end)
            add_segment(0,(x,y),end,.20,n)
            via(n,*end,.55,.3)
            placed_vias.append(end)
            for l in range(len(layers)): add_segment(l,end,end,.55,n)
            ends[j]=(*ep[:2],end,(1,) if n!='GND' else (0,1,2))

    north = next(p[2] for p in endpoints['3V3'] if p[:2]==('U4','16'))
    west = next(p[2] for p in endpoints['3V3'] if p[:2]==('U4','4'))
    manual = [north,(north[0],28.5),(39.8,28.5),(39.8,west[1]),west]
    track('3V3', k.In2_Cu,.25,*manual)
    for a,z in zip(manual,manual[1:]): add_segment(1,a,z,.25,'3V3')

    track('GND',k.F_Cu,.2,(46,33.3),(45,33.625),(44.1375,33.625))
    add_segment(0,(46,33.3),(45,33.625),.2,'GND')
    add_segment(0,(45,33.625),(44.1375,33.625),.2,'GND')
    for n,ref,pin,end in [('GND','C11','2',(35.75,29.25)),
                          ('GND','U1','2',(32.0,22.4)),
                          ('GND','C12','2',(55.75,29.35)),
                          ('GND','U2','2',(52.1,22.4)),
                          ('3V3','U1','1',(33.5,21.5)),
                          ('3V3','U1','5',(38.1,22.4)),
                          ('S1_BUF','U1','4',(38.75,29.6)),
                          ('S1_BUF','R21','1',(31.95,19.5))]:
        ends=endpoints[n]
        j=next(i for i,p in enumerate(ends) if p[:2]==(ref,pin))
        ep=ends[j]
        starts=ep[2]
        if pin=='2' and ref in ('U1','U2') or ref=='U1' and pin=='5':
            points=[starts,(end[0],starts[1]),end]
        else:
            points=[starts,end]
        track(n,k.F_Cu,.22,*points)
        for a,z in zip(points,points[1:]):
            add_segment(0,a,z,.22,n)
        via(n,*end,.65,.3)
        placed_vias.append(end)
        for l in range(len(layers)): add_segment(l,end,end,.65,n)
        ends[j]=(*ep[:2],end,(1,2))

    for n,pin in [('S2_SHUNT_HI','1'),('S2_5V','2')]:
        ends=endpoints[n]
        j=next(i for i,p in enumerate(ends) if p[:2]==('R12',pin))
        ep=ends[j]
        x,y=ep[2]; end=(40.5,y)
        track(n,k.F_Cu,.25,ep[2],end)
        add_segment(0,ep[2],end,.25,n)
        via(n,*end,.65,.3)
        placed_vias.append(end)
        for l in range(len(layers)): add_segment(l,end,end,.65,n)
        ends[j]=(*ep[:2],end,(1,2))

    def inside(x,y,r=.65):
        u,v=x*STEP,y*STEP
        return r<=u<=100-r and r<=v<=73-r and not (u<11+r and 42-r<v<52+r)
    def allowed(table,x,y,n):
        a=table.get((x,y))
        return a is None or a=={n}
    def candidates(ep, n):
        _,_,(x,y),ls=ep
        return {(u,v,l) for l in ls for u in range(grid(x)-1,grid(x)+2)
                for v in range(grid(y)-1,grid(y)+2)
                if hypot(u*STEP-x,v*STEP-y)<=.29 and inside(u,v)
                and allowed(fixed[l],u,v,n)}
    def search(starts, targets, n, margin):
        if not starts or not targets: return []
        allpts=starts|targets
        x0=min(x for x,y,l in allpts)-margin
        x1=max(x for x,y,l in allpts)+margin
        y0=min(y for x,y,l in allpts)-margin
        y1=max(y for x,y,l in allpts)+margin
        def h(x,y,l):
            return min(max(abs(x-u),abs(y-v))+.4142*min(abs(x-u),abs(y-v))+(l!=z)
                       for u,v,z in targets)
        q=[]; prev={p:None for p in starts}; costs={p:0 for p in starts}
        for x,y,l in sorted(starts): heappush(q,(h(x,y,l),0,(x,y,l)))
        while q:
            _,cost,p=heappop(q)
            if cost!=costs[p]: continue
            if p in targets:
                path=[]
                while p is not None:
                    path.append(p);p=prev[p]
                return path[::-1]
            x,y,l=p
            def push(u,v,z,c):
                s=(u,v,z);g=cost+c
                if g>=costs.get(s,float('inf')): return
                costs[s]=g;prev[s]=p;heappush(q,(g+1.12*h(u,v,z),g,s))
            for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]:
                u,v=x+dx,y+dy
                if not (x0<=u<=x1 and y0<=v<=y1 and inside(u,v)): continue
                if not allowed(fixed[l],u,v,n): continue
                if dx and dy and (not allowed(fixed[l],x,v,n) or not allowed(fixed[l],u,y,n)): continue
                push(u,v,l,(1.4142 if dx and dy else 1)+(.27 if l==2 else .035 if l==1 else 0))
            if inside(x,y,.85) and all(allowed(table,x,y,n) for table in viaspace) and all(hypot(x*STEP-a,y*STEP-b)>=.57 for a,b in placed_vias):
                for z in range(len(layers)):
                    if l!=z: push(x,y,z,7 if z<2 else 8)
        return []

    def line(n,l,a,z):
        if a==z: return
        track(n,layers[l],WIDTH,a,z)
        add_segment(l,a,z,WIDTH,n)
    def endpoint_route(n,a,z,margin):
        path=search(candidates(a,n),candidates(z,n),n,margin)
        if not path:
            return False
        begin=path[0]
        line(n,begin[2],a[2],(begin[0]*STEP,begin[1]*STEP))
        current=begin
        for i in range(1,len(path)):
            old=path[i-1]; p=path[i]
            if old[2]!=p[2]:
                line(n,old[2],(current[0]*STEP,current[1]*STEP),(old[0]*STEP,old[1]*STEP))
                via(n,p[0]*STEP,p[1]*STEP,.65,.3)
                placed_vias.append((p[0]*STEP,p[1]*STEP))
                for l in range(len(layers)): add_segment(l,(p[0]*STEP,p[1]*STEP),(p[0]*STEP,p[1]*STEP),.65,n)
                current=p
            elif i==len(path)-1 or (path[i+1][0]-p[0],path[i+1][1]-p[1],path[i+1][2]-p[2])!=(p[0]-old[0],p[1]-old[1],0):
                line(n,p[2],(current[0]*STEP,current[1]*STEP),(p[0]*STEP,p[1]*STEP))
                current=p
        end=path[-1]
        line(n,end[2],(end[0]*STEP,end[1]*STEP),z[2])
        return True

    already = {
        '3V3': [{('U4','4'),('U4','16')}],
        'BAT_RAW': [{('J1','2'),('MOD1','6'),('MOD1','12'),('U5','5')}],
        'BUCK_5V': [{('J3','1'),('MOD1','3'),('MOD1','4'),('MOD1','9'),('MOD1','10')}],
        'BUCK_FAULT': [{('U7','4'),('R48','1')}],
        'EXT_5V': [{('U5','6'),('J3','3')}],
        'PICO_VSYS': [{('D1','1'),('J11','19')}],
        'LED_5V': [{('D1','2'),('J3','2'),('C2','1'),*((f'F{i}','1') for i in range(1,4))}],
    }
    for i in range(1,4):
        already[f'S{i}_SHUNT_HI']=[{(f'F{i}','2'),(f'R{10+i}','1')}]
        already[f'S{i}_5V']=[{(f'R{10+i}','2'),(f'J{20+i}','2')}]
    # Sense lines land at the shunt itself, not elsewhere in the power tree.
    for i in (2,1,3):
        for net,pin in [(f'S{i}_5V','2'),(f'S{i}_SHUNT_HI','1')]:
            pads=endpoints[net]
            sense=next(p for p in pads if p[0]=='U4')
            shunt=next(p for p in pads if p[:2]==(f'R{10+i}',pin))
            if endpoint_route(net,sense,shunt,52):
                already[net][0].add(sense[:2])
            else:
                print('Kelvin route needs attention:',net,flush=True)
    jobs=[]
    for net,pads in endpoints.items():
        if net=='GND': continue
        clusters=[g.copy() for g in already.get(net,[])]
        for p in pads:
            if not any(p[:2] in g for g in clusters): clusters.append({p[:2]})
        def rank(a,z):
            return hypot(a[2][0]-z[2][0],a[2][1]-z[2][1])
        while len(clusters)>1:
            options=[]
            for i,a in enumerate(clusters):
                for j,z in enumerate(clusters[i+1:],i+1):
                    for x in pads:
                        if x[:2] not in a: continue
                        for y in pads:
                            if y[:2] in z: options.append((rank(x,y),i,j,x,y))
            length,i,j,a,z=min(options)
            jobs.append((length,net,a,z))
            clusters[i]|=clusters.pop(j)
    failed=[]
    for length,n,a,z in sorted(jobs,key=lambda j: (j[1] not in ('GP4','GP5','GP6','S2_5V','I2C_SDA','I2C_SCL'), not any(p[0]=='U4' for p in j[2:]),j[0])):
        if not endpoint_route(n,a,z,28):
            failed.append((n,a,z))
    for n,a,z in failed:
        if not endpoint_route(n,a,z,72):
            print('Unrouted:',n,a[:2],z[:2],flush=True)
    # SMT ground pads get local vias. Through-hole returns are joined by the ground pours.
    grounded=[p for p in endpoints['GND'] if len(p[3])>1]
    for ep in sorted(endpoints['GND'],key=lambda e:e[0]):
        if len(ep[3])!=1 or ep[:2] in (('U4','17'),('U5','8')): continue
        x,y=ep[2]
        target=[]
        for u in range(grid(x)-9,grid(x)+10):
            for v in range(grid(y)-9,grid(y)+10):
                if inside(u,v,.85) and all(allowed(table,u,v,'GND') for table in viaspace) and all(hypot(u*STEP-a,v*STEP-b)>=.57 for a,b in placed_vias):
                    target.append((hypot(u*STEP-x,v*STEP-y),u,v))
        for _,u,v in sorted(target)[:35]:
            if endpoint_route('GND',ep,('via','0',(u*STEP,v*STEP),(0,)),8):
                via('GND',u*STEP,v*STEP,.65,.3)
                placed_vias.append((u*STEP,v*STEP))
                for l in range(len(layers)): add_segment(l,(u*STEP,v*STEP),(u*STEP,v*STEP),.65,'GND')
                grounded.append(ep)
                break
        else:
            for z in sorted(grounded,key=lambda p:hypot(x-p[2][0],y-p[2][1]))[:8]:
                if endpoint_route('GND',ep,z,22):
                    grounded.append(ep)
                    break
