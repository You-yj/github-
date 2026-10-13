(() => {
  "use strict";
  const NS = "http://www.w3.org/2000/svg";
  const $ = (id) => document.getElementById(id);
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const lerp = (a, b, t) => a + (b - a) * t;
  const ease = (t) => { const x = clamp(t); return x * x * (3 - 2 * x); };
  const ramp = (t, a, b) => ease((t - a) / (b - a));
  const reduced = matchMedia("(prefers-reduced-motion: reduce)");
  const svg = (tag, attrs = {}, parent) => {
    const node = document.createElementNS(NS, tag);
    Object.entries(attrs).forEach(([k, v]) => node.setAttribute(k, String(v)));
    if (parent) parent.appendChild(node);
    return node;
  };
  const textSvg = (parent, x, y, value, attrs = {}) => {
    const node = svg("text", { x, y, ...attrs }, parent);
    node.textContent = value;
    return node;
  };
  const m = (body) => `<math xmlns="http://www.w3.org/1998/Math/MathML" display="block"><mrow>${body}</mrow></math>`;
  const mi = (v) => `<mi>${v}</mi>`;
  const mo = (v) => `<mo>${v}</mo>`;
  const mn = (v) => `<mn>${v}</mn>`;
  const E = `<mover>${mi("E")}${mo("→")}</mover>`;
  const tvec = `<mover>${mi("t")}${mo("→")}</mover>`;
  const sub = (body, index) => `<msub>${body}${index}</msub>`;
  const eh = sub(E, mi("h"));
  const localEh = (k) => `<mrow>${eh}${mo("|")}${sub(mi("K"),mn(k))}</mrow>`;
  const math = {
    domain: m(`${E}${mo(":")}${mi("Ω")}${mo("→")}${msupR(2)}`),
    restriction: m(`${E}${mo("↦")}${mo("{")}${E}${mo("|")}${sub(mi("K"), mi("i"))}${mo("}")}`),
    local: m(`${sub(E,mn(1))}${mo("=")}${E}${mo("|")}${sub(mi("K"),mn(1))}${mo(",")}${sub(E,mn(2))}${mo("=")}${E}${mo("|")}${sub(mi("K"),mn(2))}`),
    localSpace: m(`${sub(mi("N"),mn(0))}${mo("(")}${mi("K")}${mo(")")}${mo("=")}${mo("{")}${mi("a")}${mo("+")}${mi("b")}${mo("(")}${mo("−")}${mi("y")}${mo(",")}${mi("x")}${mo(")")}${mo("}")}`),
    geometry: m(`${sub(mi("K"),mn(1))}${mo("∩")}${sub(mi("K"),mn(2))}${mo("=")}${mi("e")}`),
    tangent: m(`${mo("(")}${localEh(1)}${mo("−")}${localEh(2)}${mo(")")}${mo("·")}${tvec}${mo("=")}${mn(0)}`),
    dof: m(`${sub(mi("d"),mi("e"))}${mo("(")}${eh}${mo(")")}${mo("=")}${msubInt("e")}${eh}${mo("·")}${sub(tvec,mi("e"))}${mi("ds")}`),
    basis: m(`${sub(mi("d"),mi("e"))}${mo("(")}${sub(mi("N"),mi("e′"))}${mo(")")}${mo("=")}${sub(mi("δ"),mi("e,e′"))}`),
    lagrangeBasis: m(`${sub(mi("φ"),mi("i"))}${mo("(")}${sub(mi("a"),mi("j"))}${mo(")")}${mo("=")}${sub(mi("δ"),mi("ij"))}`),
    orientation: m(`${sub(mi("d"),mi("b→a"))}${mo("(")}${eh}${mo(")")}${mo("=")}${mo("−")}${sub(mi("d"),mi("a→b"))}${mo("(")}${eh}${mo(")")}`),
    piola: m(`${msubInt("e")}${eh}${mo("·")}${tvec}${mi("ds")}${mo("=")}${msubInt("ê")}${moverHat(eh)}${mo("·")}${moverHat(tvec)}${mi("dŝ")}`),
    global: m(`${sub(mi("V"),mi("h"))}${mo("⊂")}${mi("H")}${mo("(")}${mi("curl")}${mo(";")}${mi("Ω")}${mo(")")}`),
    A: m(`${E}${mo("=")}${mo("(")}${mi("sin πy")}${mo(",")}${mi("sin πx")}${mo(")")}`),
    B: m(`${E}${mo("=")}${mo("∇")}${mi("φ")}${mo(",")}${mi("curl")}${E}${mo("=")}${mn(0)}`),
    matrixA: m(`${mi("A")}${mo("=")}${mi("C")}${mo("+")}${mi("M")}`),
    matrixB: m(`${mi("A")}${mo("=")}${mi("C")}${mo("−")}${msup(mi("k"),mn(2))}${mi("M")}`),
    boundary: m(`${E}${mo("·")}${tvec}${mo("=")}${mi("g")}${mo("on")}${mi("∂Ω")}`),
    solve: m(`${mi("A")}${sub(mi("u"),mi("h"))}${mo("=")}${mi("b")}`),
    error: m(`${sub(`<mrow>${mo("‖")}${E}${mo("−")}${eh}${mo("‖")}</mrow>`,`<mrow>${mi("L")}${mn(2)}</mrow>`)}${mo("↓")}`)
  };
  function msupR(n) { return `<msup>${mi("ℝ")}${mn(n)}</msup>`; }
  function msup(base, exponent) { return `<msup>${base}${exponent}</msup>`; }
  function msubInt(s) { return `<msub>${mo("∫")}${mi(s)}</msub>`; }
  function moverHat(v) { return `<mover>${v}${mo("ˆ")}</mover>`; }

  const knowledge = [
    { name: "Ⅰ · 整体电场", title: "一切从整体电场开始", text: "先看区域中的连续电场：平面中的每个位置，都对应一个二维向量。", formula: "domain", duration: 4.8 },
    { name: "Ⅰ · 场进入网格", title: "网格只是观察场的方式", text: "三角网格覆盖整个区域；每个单元看到的是同一个场在该处的限制。", formula: "restriction", duration: 5 },
    { name: "Ⅱ · 取出一个单元", title: "从整体网格进入一个三角形", text: "整体网格退到背景，只取出一个单元 K；局部场仍来自刚才的整体电场。", formula: "local", duration: 4.6 },
    { name: "Ⅱ · 局部空间", title: "一个三角形里允许怎样的场", text: "最低阶局部 Nédélec 空间由平移趋势与旋转趋势组成，适合描述带旋度的向量场。", formula: "localSpace", duration: 5.8 },
    { name: "Ⅱ · 自由度", title: "为什么读取有向边", text: "Lagrange 元读取节点值；Nédélec 棱元沿有向边读取切向积分。", formula: "dof", duration: 6 },
    { name: "Ⅱ · 基函数", title: "一条边对应一个局部基函数", text: "选择一条边：目标边的切向读数为 1，其余两条边为 0，内部场随之连续变化。", formula: "basis", duration: 6 },
    { name: "Ⅲ · 参考元映射", title: "把同一种局部结构放到不同单元", text: "协变 Piola 映射改变三角形形状，同时保持对应有向边的切向积分。", formula: "piola", duration: 7 },
    { name: "Ⅲ · 物理单元拼合", title: "映射后的单元先在几何上相邻", text: "从物理网格中取出两个相邻单元并合拢；此时公共边只是位置重合，还没有完成函数空间的拼接。", formula: "geometry", duration: 6.4 },
    { name: "Ⅲ · 方向与连续", title: "统一方向后，公共边切向连续", text: "先把两侧局部边方向换算到同一全局方向，再共享边自由度，最低阶切向迹随之匹配。", formula: "orientation", duration: 8.2 },
    { name: "Ⅲ · 全局空间", title: "局部场拼成全局棱元空间", text: "映射、方向校正与公共边共享共同构成全局 Nédélec 棱元空间。", formula: "global", duration: 5.2 }
  ];
  const examples = {
    A: { label: "模型 A · 完整验收", file: "run_curlcurl_plus.py", note: "旋度非零；齐次切向边界；可验收双旋度项组装。", errors: [0.222455,0.112834,0.056615,0.028332], curls: [0.439528,0.223136,0.111985,0.056045] },
    B: { label: "模型 B · Maxwell 形态", file: "run_curlcurl_minus.py", note: "制造场旋度恒为零；可练习负质量项与非齐次切向边界，不能单独验收双旋度项。", errors: [0.266939,0.137448,0.069244,0.034688], curls: [0.001188961,0.0002912822,0.00007184052,0.00001788652] }
  };
  const implementation = [
    { name: "制造解", title: "先有真解，再验离散解", text: "由前页示意场转入程序的解析电场，代入方程反推出源项。", formula: model => model === "A" ? "A" : "B", code: model => model === "A" ? "def exact_field(points):\n    return bm.stack((bm.sin(bm.pi*points[...,1]),\n                     bm.sin(bm.pi*points[...,0])), axis=-1)" : "def exact_field(points):\n    x, y = points[...,0], points[...,1]\n    return bm.stack((bm.sin(bm.pi*x)*bm.cos(bm.pi*y),\n                     bm.cos(bm.pi*x)*bm.sin(bm.pi*y)), axis=-1)" },
    { name: "网格", title: "让区域成为三角网格", text: "顶点、单元、边和边界组成计算骨架。", formula: () => "restriction", code: () => "mesh = TriangleMesh.from_box(\n    [0, 1, 0, 1], nx=n, ny=n\n)" },
    { name: "棱元空间", title: "每条全局边对应一个读数", text: "最低阶第一类 Nédélec 空间将边切向测量组织成全局自由度。", formula: () => "dof", code: () => "space = FirstNedelecFESpace(mesh, p=0)\ndofs = space.number_of_global_dofs()" },
    { name: "组装矩阵", title: "旋度项与质量项进入矩阵", text: "两个模型共用组装接口；系统矩阵的质量项符号不同。", formula: model => model === "A" ? "matrixA" : "matrixB", code: model => "C = curl_form.assembly()\nM = mass_form.assembly()\n" + (model === "A" ? "A = C + M" : "A = C - (WAVENUMBER**2) * M") },
    { name: "组装右端", title: "源项变成离散右端", text: "制造解决定源项，源项积分器把连续数据投到测试空间。", formula: () => "solve", code: () => "source_form = LinearForm(space)\nsource_form.add_integrator(\n    VectorSourceIntegrator(source, q=6)\n)\nb = source_form.assembly()" },
    { name: "切向边界", title: "只约束边界切向自由度", text: "模型 A 用零边界；模型 B 用解析场给出的非零切向数据。", formula: () => "boundary", code: model => model === "A" ? "A_bc, b_bc = DirichletBC(\n    space, gd=bm.zeros(dofs)\n).apply(A, b)" : "A_bc, b_bc = DirichletBC(\n    space, gd=tangential_boundary_data\n).apply(A, b)" },
    { name: "求解", title: "求解全局边未知数", text: "边自由度可重建数值场；蓝色解析场是参照，橙色边读数是过程示意。", formula: () => "solve", code: () => "uh = spsolve(A_bc, b_bc, solver=\"scipy\")\nresidual_vec = A_bc.matmul(uh) - b_bc" },
    { name: "误差验证", title: "看误差随网格加密下降", text: "残差检验线性系统；场误差与旋度误差检验离散逼近。", formula: () => "error", code: () => "dE = space.value(uh, bcs) - exact_field(points)\ndC = space.curl_value(uh, bcs) - exact_curl(points)" }
  ];

  const state = { page:0, stage:0, requestedStage:0, p:0, playing:false, playAfterSeek:false, ambientPaused:false, last:0, implMeshWasGrowing:false, model:"A", normalLeft:1.2, normalRight:-.6, basisEdge:0, basisNode:0, basisComponent:0, basisMode:"edge", basisTransition:null, reverse:false, skew:0, seeking:null };
  const scene = [$("cover"), $("knowledge"), $("implementation")];
  const stageList = $("stageList");
  let lastStageIndicator="";
  const line = (parent,x1,y1,x2,y2,attrs={}) => svg("line",{x1,y1,x2,y2,...attrs},parent);
  function vector(x,y) {
    const u=13+18*Math.cos(y/92+x/310)-.016*(y-345);
    const v=-4+14*Math.sin(x/112-y/205)+.012*(x-455);
    const length=Math.hypot(u,v)||1;
    const size=15+Math.min(5,length*.12);
    return [u/length*size,v/length*size];
  }
  function streamline(x,y,steps=42){
    let d=`M${x.toFixed(1)} ${y.toFixed(1)}`;
    for(let i=0;i<steps;i++){
      const [u,v]=vector(x,y);x+=u*.56;y+=v*.56;
      if(x<80||x>1170||y<54||y>660)break;
      d+=` L${x.toFixed(1)} ${y.toFixed(1)}`;
    }
    return d;
  }
  function exactVector(model,x,y){
    return model==="A"
      ? [Math.sin(Math.PI*y),Math.sin(Math.PI*x)]
      : [Math.sin(Math.PI*x)*Math.cos(Math.PI*y),Math.cos(Math.PI*x)*Math.sin(Math.PI*y)];
  }
  function buildImplementationField(){
    for(const model of ["A","B"]){
      const host=$("implField"+model);
      const trace=(sx,sy)=>{
        const walk=sign=>{
          let x=sx,y=sy;const points=[];
          for(let i=0;i<100;i++){
            const [u,v]=exactVector(model,(x-62)/664,(520-y)/408),length=Math.hypot(u,v);
            if(length<.025)break;
            const nx=x+sign*5*u/length,ny=y-sign*5*v/length;
            if(nx<65||nx>723||ny<115||ny>517)break;
            x=nx;y=ny;points.push([x,y]);
          }
          return points;
        };
        return [...walk(-1).reverse(),[sx,sy],...walk(1)].map((point,i)=>`${i?"L":"M"}${point[0].toFixed(1)} ${point[1].toFixed(1)}`).join(" ");
      };
      let index=0;
      for(let y=150;y<=480;y+=65)for(let x=113;x<=680;x+=115){
        const d=trace(x,y);
        svg("path",{d,"class":"field-trace"},host);
        const flow=svg("path",{d,"class":"stream-flow"},host);
        flow.style.animationDelay=`-${(index++*1.17).toFixed(2)}s`;
      }
      for(let y=139;y<=489;y+=43)for(let x=91;x<=699;x+=51){
        const [u,v]=exactVector(model,(x-62)/664,(520-y)/408),length=Math.hypot(u,v);
        if(length<.045)continue;
        const arrow=line(host,x,y,x+10*u/length,y-10*v/length,{"class":"field-vector"});
        arrow.style.animationDelay=`-${((x*.013+y*.019)%3.8).toFixed(2)}s`;
      }
    }
  }

  function buildCover() {
    const field = $("coverField"), mesh = $("coverMesh"), edges = $("coverEdges");
    for(let y=70;y<690;y+=27) for(let x=430;x<1200;x+=27) {
      const [u,v]=vector(x,y), shift=9*Math.sin(x*.013+y*.019);
      const arrow=line(field,x+shift,y,x+shift+u*.66,y+v*.66,{"class":"cover-vector"});
      arrow.style.animationDelay=`${((x*.013+y*.021)%3.4).toFixed(2)}s`;
    }
    for(let y=95;y<650;y+=86)for(const x of [405,590,790])svg("path",{d:streamline(x,y,58),"class":"flow-line"},field);
    for(let j=0;j<=7;j++) for(let i=0;i<=10;i++) {
      const x=420+i*80,y=60+j*85;
      const add=(d,depth)=>{
        const path=svg("path",{d},mesh);
        path.style.setProperty("--growth-delay",`${(Math.max(0,depth)*.33).toFixed(2)}s`);
      };
      if(i<10) add(`M${x} ${y} L${x+80} ${y}`,Math.min(i+.5,9.5-i,j,7-j));
      if(j<7) add(`M${x} ${y} L${x} ${y+85}`,Math.min(i,10-i,j+.5,6.5-j));
      if(i<10&&j<7) add(`M${x} ${y} L${x+80} ${y+85}`,Math.min(i+.5,9.5-i,j+.5,6.5-j));
    }
    ["M740 315 L820 400","M820 315 L900 400","M900 315 L980 400"].forEach(d=>svg("path",{d},edges));
  }

  const meshConfig={x:112,y:105,nx:8,ny:5,dx:94,dy:94};
  function buildGlobalMesh() {
    const field=$("globalField"),mesh=$("globalMesh"),focus=$("globalFocus"),annotations=$("globalAnnotations");
    for(let y=91;y<590;y+=22) for(let x=106;x<890;x+=23) {
      const [u,v]=vector(x,y), a=line(field,x,y,x+u*.67,y+v*.67);
      a.dataset.seed=String(Math.sin(x*.13+y*.09));
      a.style.animationDelay=`${((x*.014+y*.02)%3.2).toFixed(2)}s`;
    }
    for(let y=114;y<590;y+=74)for(const x of [116,252,388,530])svg("path",{d:streamline(x,y,47),"class":"field-stream"},field);
    const c=meshConfig;
    for(let j=0;j<=c.ny;j++)for(let i=0;i<=c.nx;i++){
      const x=c.x+i*c.dx,y=c.y+j*c.dy;
      const add=(d,length,depth)=>svg("path",{d,"data-length":length.toFixed(2),"data-depth":Math.max(0,depth).toFixed(2)},mesh);
      if(i<c.nx) add(`M${x} ${y} H${x+c.dx}`,c.dx,Math.min(i+.5,c.nx-i-.5,j,c.ny-j));
      if(j<c.ny) add(`M${x} ${y} V${y+c.dy}`,c.dy,Math.min(i,c.nx-i,j+.5,c.ny-j-.5));
      if(i<c.nx&&j<c.ny) add(`M${x} ${y+c.dy} L${x+c.dx} ${y}`,Math.hypot(c.dx,c.dy),Math.min(i+.5,c.nx-i-.5,j+.5,c.ny-j-.5));
    }
    const x=c.x+3*c.dx,y=c.y+2*c.dy;
    svg("polygon",{points:`${x},${y} ${x+c.dx},${y} ${x},${y+c.dy}`},focus);
    svg("polygon",{points:`${x+c.dx},${y} ${x+c.dx},${y+c.dy} ${x},${y+c.dy}`},focus);
    [[1,1,"E|K₁"],[5,1,"E|K₂"],[2,3,"E|K₃"],[6,3,"E|K₄"]].forEach(([i,j,label])=>textSvg(annotations,c.x+i*c.dx+19,c.y+j*c.dy+54,label,{"class":"grid-annotation"}));
    for(let y=10;y<210;y+=22)for(let x=10;x<210;x+=22){
      const [u,v]=vector(x+330,y+230);
      for(const id of ["leftLocalField","rightLocalField"]){
        line($(id),x,y,x+u*.5,y+v*.5,{"data-base-x2":(x+u*.5).toFixed(2),"data-base-y2":(y+v*.5).toFixed(2)});
      }
    }
    for(let y=16;y<210;y+=15)for(let x=16;x<210;x+=15){
      const [u,v]=vector(x+330,y+230);
      for(const id of ["leftLocalField","rightLocalField"]){
        line($(id),x,y,x+u*.39,y+v*.39,{"class":"local-extra","data-base-x2":(x+u*.39).toFixed(2),"data-base-y2":(y+v*.39).toFixed(2)});
      }
    }
    for(let y=13;y<215;y+=32)for(const x of [4,58,112,166]){
      let px=x,py=y,d=`M${px} ${py}`;
      for(let i=0;i<32;i++){
        const [u,v]=vector(px+330,py+230);
        px+=u*.49;py+=v*.49;
        if(px<0||px>220||py<0||py>220)break;
        d+=` L${px.toFixed(1)} ${py.toFixed(1)}`;
      }
      for(const id of ["leftLocalField","rightLocalField"]){
        const stream=svg("path",{d,"class":"local-stream"},$(id));
        stream.style.animationDelay=`-${((x*.027+y*.031)%10).toFixed(2)}s`;
      }
    }
    ["leftLocal","rightLocal"].forEach(id=>svg("path",{d:"M220 0 L0 220",stroke:"#f0ad76","stroke-width":3,fill:"none",opacity:.8},$(id)));
    const leftCue=svg("g",{id:"leftEdgeCue","class":"edge-cue"},$("leftLocal"));
    const rightCue=svg("g",{id:"rightEdgeCue","class":"edge-cue"},$("rightLocal"));
    line(leftCue,164,63,127,100,{stroke:"#77e4df","stroke-width":3,"marker-end":"url(#fineArrow)"});
    line(rightCue,165,112,128,149,{id:"rightTangentArrow",stroke:"#77e4df","stroke-width":3,"marker-end":"url(#fineArrow)"});
    line(leftCue,105,113,77,85,{stroke:"#c9a8d9","stroke-width":2.4,"marker-end":"url(#fineArrow)"});
    line(rightCue,153,144,192,183,{id:"rightNormalArrow",stroke:"#c9a8d9","stroke-width":2.4,"marker-end":"url(#fineArrow)"});
    textSvg(leftCue,99,111,"t₁",{"class":"edge-cue-label",fill:"#a4f5eb"});
    textSvg(rightCue,176,176,"t₂",{"class":"edge-cue-label",fill:"#a4f5eb"});
    buildCompare();buildAssembly();buildPiola();buildStitch();buildFinal();
  }

  function buildCompare() {
    const host=$("compareLayer");
    for(const side of [0,1]){
      const g=svg("g",{id:side?"comparisonRight":"comparisonLeft",transform:`translate(${side?486:120} 158)`},host);
      svg("path",{id:side?"rightLowerTri":"leftLowerTri",d:"M20 292 L310 292 L310 28 Z",fill:side?"rgba(38,146,145,.15)":"rgba(117,111,146,.16)",stroke:side?"#69d6c9":"#b4a9cb","stroke-width":2},g);
      svg("path",{d:"M20 292 L20 28 L310 28 Z",fill:side?"rgba(38,146,145,.1)":"rgba(117,111,146,.1)",stroke:side?"#69d6c9":"#b4a9cb","stroke-width":2},g);
      svg("path",{d:"M20 292 L310 28",stroke:"#f0ad76","stroke-width":side?4:2.5,fill:"none","stroke-dasharray":side?"":"6 6"},g);
      textSvg(g,20,-8,side?"NÉDÉLEC · 有向边":"LAGRANGE · 节点",{"class":"svg-label","font-size":19,fill:side?"#81dacf":"#c4b6da"});
      const info=svg("g",{id:side?"compareEdgeInfo":"compareNodeInfo"},g);
      if(side){
        for(let j=0;j<6;j++){const s=j/6;const x=35+245*s,y=278-224*s;line(info,x,y,x+15,y-14,{stroke:"#f6b379","stroke-width":2,"marker-end":"url(#warmArrow)"});}
        textSvg(info,63,345,"共享：沿边切向测量",{"class":"svg-label","font-size":17,fill:"#a9e5dc"});
      }else{
        [[20,28],[20,292],[310,28],[310,292]].forEach(([x,y])=>{svg("circle",{cx:x,cy:y,r:7,fill:"#b9a5d0"},info);line(info,x,y,x+17,y-10,{stroke:"#b9a5d0","stroke-width":2,"marker-end":"url(#fineArrow)"});});
        textSvg(info,42,345,"共享：节点完整向量",{"class":"svg-label","font-size":17,fill:"#cec0d8"});
      }
      const normal=svg("g",{id:side?"rightNormalComparison":"leftNormalComparison"},g);
      line(normal,130,166,151,187,{stroke:"#b9a9cf","stroke-width":2,"marker-end":"url(#fineArrow)"});
      line(normal,176,128,side?214:198,side?166:150,{id:side?"rightNormalB":"leftNormalB",stroke:"#b9a9cf","stroke-width":2,"marker-end":"url(#fineArrow)"});
      textSvg(normal,side?65:70,378,side?"法向仍可不同":"法向被一并约束",{fill:side?"#9adccf":"#d6bdd4","font-size":17});
      const basis=svg("g",{id:side?"compareEdgeBasis":"compareNodeBasis"},g);
      for(let y=57;y<274;y+=25)for(let x=47;x<292;x+=26){
        const lb=(x-20)/290,lc=(y-28)/264;
        if(lb+lc<.92)line(basis,x,y,x,y,{"data-x":x,"data-y":y,stroke:side?"#7ed7cc":"#beaed1","stroke-width":1.2,"marker-end":"url(#fineArrow)",opacity:.78});
      }
      const ghost=basis.cloneNode(true);
      ghost.id=side?"compareEdgeBasisGhost":"compareNodeBasisGhost";
      g.insertBefore(ghost,basis);
      if(side){
        svg("path",{id:"selectedBasisEdge",d:"M20 28 H310",stroke:"#f7c08c","stroke-width":5,fill:"none"},g);
        textSvg(g,76,414,"d₁₂ = 1   d₂₃ = 0   d₃₁ = 0",{id:"compareEdgeRead",fill:"#dfefe8","font-size":18,"font-family":"var(--math)"});
        svg("path",{id:"selectedBasisEdgeGhost",d:"M20 28 H310",stroke:"#f7c08c","stroke-width":5,fill:"none",opacity:0},g);
        textSvg(g,76,414,"",{id:"compareEdgeReadGhost",fill:"#dfefe8","font-size":18,"font-family":"var(--math)",opacity:0});
      }else{
        svg("circle",{id:"selectedBasisNode",cx:20,cy:28,r:11,fill:"#f7c08c"},g);
        textSvg(g,75,414,"节点 1：x 分量 = 1；其余 = 0",{id:"compareNodeRead",fill:"#e5d9e8","font-size":17});
        svg("circle",{id:"selectedBasisNodeGhost",cx:20,cy:28,r:11,fill:"#f7c08c",opacity:0},g);
        textSvg(g,75,414,"",{id:"compareNodeReadGhost",fill:"#e5d9e8","font-size":17,opacity:0});
      }
    }
  }

  function buildAssembly() {
    const host=$("assemblyLayer"),c=meshConfig;
    const pair=svg("g",{id:"assemblyPair",transform:"translate(290 145) scale(1.7)"},host);
    svg("path",{d:"M0 0 L220 0 L0 220 Z",fill:"rgba(72,132,175,.22)",stroke:"#78b8db","stroke-width":2},pair);
    svg("path",{d:"M220 0 L220 220 L0 220 Z",fill:"rgba(54,168,152,.19)",stroke:"#70d6c9","stroke-width":2},pair);
    for(const [side,clip,color] of [[0,"leftTriClip","#83cce2"],[1,"rightTriClip","#88dcca"]]){
      const sample=svg("g",{"clip-path":`url(#${clip})`},pair);
      for(let y=15;y<211;y+=22)for(let x=15;x<211;x+=22){
        const [u,v]=vector(x+330,y+230);
        line(sample,x,y,x+u*.44+(side?1.4:-1.4),y+v*.44+(side?1.4:-1.4),{stroke:color,"stroke-width":1.15,"marker-end":"url(#fineArrow)"});
      }
    }
    const localDirections=svg("g",{id:"pairLocalDirections"},pair);
    line(localDirections,185,31,151,65,{id:"pairLocalOne",stroke:"#f9c19a","stroke-width":2.8,"marker-end":"url(#warmArrow)"});
    line(localDirections,75,150,109,116,{id:"pairLocalTwo",stroke:"#f9c19a","stroke-width":2.8,"marker-end":"url(#warmArrow)"});
    line(pair,216,4,5,215,{id:"pairGlobalArrow",stroke:"#f0ad76","stroke-width":3,"marker-end":"url(#warmArrow)"});
    textSvg(pair,22,58,"局部边 ①",{fill:"#c4e4ee","font-size":18});
    textSvg(pair,115,191,"局部边 ②",{fill:"#bcece1","font-size":18});
    textSvg(pair,72,253,"+  与  −  →  同一全局 dₑ",{id:"pairDirectionRead",fill:"#f7c79f","font-size":17,"font-family":"var(--math)"});
    for(let j=0;j<5;j++)for(let i=0;i<7;i++){
      const x=c.x+i*c.dx+47,y=c.y+j*c.dy+47;
      if((i+j)%2===0){
        const g=svg("g",{"data-wave":String(i+j),"data-sign":String((i+j)%4===0?1:-1),"data-x":x,"data-y":y},host);
        const reverse=(i+j)%4===0;
        line(g,x-16,y+16,x+15,y-15,{"data-x1":x-16,"data-y1":y+16,"data-x2":x+15,"data-y2":y-15,stroke:"#f0ad76","stroke-width":2.2,"marker-end":"url(#warmArrow)"});
        textSvg(g,x+19,y+8,reverse?"+":"−",{fill:reverse?"#b8efe4":"#f6b379","font-size":22,"font-family":"var(--math)"});
        svg("circle",{cx:x,cy:y,r:4.5,fill:"#f0ad76","class":"global-edge-dot",opacity:0},g);
        textSvg(g,x+9,y-8,`e${j*7+i+1}`,{"class":"global-edge-id",fill:"#f6c99f","font-size":14,opacity:0});
      }
    }
  }

  function buildStitch() {
    const host=$("stitchLayer");
    const left=svg("g",{id:"stitchLeftCell"},host),right=svg("g",{id:"stitchRightCell"},host);
    svg("path",{d:"M0 110 L220 0 L220 220 Z",fill:"rgba(72,132,175,.2)",stroke:"#78b8db","stroke-width":2.2},left);
    svg("path",{d:"M0 0 L0 220 L220 110 Z",fill:"rgba(54,168,152,.18)",stroke:"#70d6c9","stroke-width":2.2},right);
    const leftField=svg("g",{"clip-path":"url(#stitchLeftClip)",class:"stitch-field"},left);
    const rightField=svg("g",{"clip-path":"url(#stitchRightClip)",class:"stitch-field"},right);
    for(let y=18;y<=202;y+=20)for(let x=18;x<=202;x+=20){
      const v=10+2.5*Math.sin(y*.055);
      if(x>=2*Math.abs(y-110))line(leftField,x,y,x+8.5,y+v,{stroke:"#83cce2","stroke-width":1.05,"marker-end":"url(#tinyArrow)",class:"stitch-field-vector"});
      if(x<=220-2*Math.abs(y-110))line(rightField,x,y,x-4.5,y+v,{stroke:"#88dcca","stroke-width":1.05,"marker-end":"url(#tinyArrow)",class:"stitch-field-vector"});
    }
    svg("path",{id:"stitchLeftEdge",d:"M220 0 V220",stroke:"#f0ad76","stroke-width":5,fill:"none"},left);
    svg("path",{id:"stitchRightEdge",d:"M0 0 V220",stroke:"#f0ad76","stroke-width":5,fill:"none"},right);
    textSvg(left,72,106,"E₁ = Eₕ|K₁",{fill:"#c6e6f0","font-size":20,"font-family":"var(--math)"});
    textSvg(right,54,106,"E₂ = Eₕ|K₂",{fill:"#c5eee5","font-size":20,"font-family":"var(--math)"});
    const localDirections=svg("g",{id:"stitchLocalDirections"},host);
    line(localDirections,416,202,416,253,{stroke:"#f8c098","stroke-width":3,"marker-end":"url(#warmArrow)"});
    line(localDirections,444,338,444,287,{stroke:"#f8c098","stroke-width":3,"marker-end":"url(#warmArrow)"});
    textSvg(localDirections,333,194,"tₖ₁,ₑ",{fill:"#f4c49f","font-size":17,"font-family":"var(--math)"});
    textSvg(localDirections,455,355,"tₖ₂,ₑ",{fill:"#f4c49f","font-size":17,"font-family":"var(--math)"});
    const directionSigns=svg("g",{id:"stitchDirectionSigns"},host);
    textSvg(directionSigns,288,432,"sₖ₁,ₑ = +1",{id:"stitchLeftSign",fill:"#bfe9e4","font-size":18,"font-family":"var(--math)"});
    textSvg(directionSigns,449,432,"sₖ₂,ₑ = −1",{id:"stitchRightSign",fill:"#f1ba91","font-size":18,"font-family":"var(--math)"});
    const tangents=svg("g",{id:"stitchTangents"},host);
    const leftTangents=svg("g",{id:"stitchLeftTangents"},tangents),rightTangents=svg("g",{id:"stitchRightTangents"},tangents);
    for(const y of [205,255,305]){
      line(leftTangents,290,y,290,y+28,{stroke:"#87dcdf","stroke-width":3,"marker-end":"url(#fineArrow)"});
      line(rightTangents,570,y,570,y+28,{stroke:"#87dcdf","stroke-width":3,"marker-end":"url(#fineArrow)"});
    }
    textSvg(tangents,327,371,"两侧沿同一 tₑ 读取",{fill:"#bfe9e4","font-size":18});
    const normals=svg("g",{id:"stitchNormals"},host);
    const leftNormal=svg("g",{id:"stitchLeftNormal"},normals),rightNormal=svg("g",{id:"stitchRightNormal"},normals);
    line(leftNormal,264,274,231,274,{stroke:"#c6a9d6","stroke-width":2.4,"marker-end":"url(#fineArrow)"});
    line(rightNormal,587,274,610,274,{stroke:"#c6a9d6","stroke-width":2.4,"marker-end":"url(#fineArrow)"});
    textSvg(normals,309,408,"法向分量仍可以不同",{fill:"#cbb9d7","font-size":18});
    textSvg(host,280,470,"几何位置重合  ≠  已经切向连续",{id:"stitchGeometryNote",fill:"#d7c5d8","font-size":20,"font-family":"var(--serif)"});
    const lock=svg("g",{id:"stitchLock"},host);
    line(lock,430,164,430,376,{id:"stitchGlobalArrow",stroke:"#ffd0a8","stroke-width":3.2,"marker-end":"url(#warmArrow)"});
    for(const y of [182,226,270,314,358])svg("circle",{cx:430,cy:y,r:4.5,fill:"#f0ad76"},lock);
    textSvg(lock,450,285,"全局方向 tₑ · 共享 dₑ",{fill:"#f6c397","font-size":18});
    const statement=svg("g",{id:"stitchStatement"},host);
    textSvg(statement,150,502,"dₑ(E₁) = dₑ(E₂)",{fill:"#f5c79f","font-size":25,"font-family":"var(--math)"});
    textSvg(statement,350,502,"⟹",{fill:"#f0ad76","font-size":26,"font-family":"var(--math)"});
    textSvg(statement,394,502,"(E₁ − E₂) · tₑ = 0",{fill:"#e4f4ee","font-size":25,"font-family":"var(--math)"});
    textSvg(statement,155,545,"最低阶：切向迹在边上是常数，因此一个共享读数即可锁定整条边",{fill:"#a9cfd0","font-size":16});
  }

  function buildPiola() {
    const host=$("piolaLayer");
    const one=svg("g",{id:"piolaOne"},host);
    svg("path",{d:"M100 490 L315 490 L100 230 Z",fill:"rgba(66,136,174,.18)",stroke:"#7cb8d7","stroke-width":3},one);
    textSvg(one,118,211,"参考单元  K̂",{"class":"svg-label","font-size":23});
    for(let y=275;y<475;y+=28)for(let x=120;x<290;x+=27)if(x+y<596)line(one,x,y,x+13,y-8,{stroke:"#7bc8d3","stroke-width":1.4,"marker-end":"url(#fineArrow)"});
    const phys=svg("g",{id:"piolaPhysical"},one);
    svg("path",{id:"piolaPhysicalTriangle",d:"M420 490 L700 490 L545 218 Z",fill:"rgba(53,171,159,.18)",stroke:"#75dbc9","stroke-width":3},phys);
    const physicalField=svg("g",{id:"piolaPhysicalField"},phys);
    for(let s=.12;s<.86;s+=.12)for(let r=.12;r<.86-s;r+=.13){
      line(physicalField,0,0,0,0,{"data-r":r.toFixed(3),"data-s":s.toFixed(3),stroke:"#8bdccc","stroke-width":1.55,"marker-end":"url(#fineArrow)"});
    }
    textSvg(one,440,211,"物理单元  K",{"class":"svg-label","font-size":23});
    svg("path",{d:"M325 353 L405 353",stroke:"#f0ad76","stroke-width":2,"marker-end":"url(#warmArrow)"},one);
    const many=svg("g",{id:"piolaMany"},host),c=meshConfig;
    const node=(i,j)=>{
      const inner=i>0&&i<c.nx&&j>0&&j<c.ny;
      return [c.x+i*c.dx+(inner?11*Math.sin(i*1.8+j*1.1):0),c.y+j*c.dy+(inner?9*Math.cos(i*.9+j*1.6):0)];
    };
    for(let j=0;j<c.ny;j++)for(let i=0;i<c.nx;i++){
      const a=node(i,j),b=node(i+1,j),c1=node(i,j+1),d=node(i+1,j+1);
      const cellX=(a[0]+b[0]+c1[0]+d[0])/4,cellY=(a[1]+b[1]+c1[1]+d[1])/4;
      const cell=svg("g",{"data-wave":String(i+j),"data-x":cellX.toFixed(2),"data-y":cellY.toFixed(2)},many);
      [[a,b,c1],[b,d,c1]].forEach((tri,k)=>{
        svg("polygon",{points:tri.map(p=>p.join(",")).join(" "),fill:k?"rgba(46,155,153,.13)":"rgba(77,131,165,.14)",stroke:"#78c4bf","stroke-width":1.15},cell);
        const mx=(tri[0][0]+tri[1][0]+tri[2][0])/3,my=(tri[0][1]+tri[1][1]+tri[2][1])/3;
        line(cell,mx-7,my+4,mx+8,my-5,{stroke:"#8bd8d4","stroke-width":1.15,"marker-end":"url(#fineArrow)"});
      });
      const edgeMark=line(cell,b[0]*.68+c1[0]*.32,b[1]*.68+c1[1]*.32,b[0]*.32+c1[0]*.68,b[1]*.32+c1[1]*.68,{"class":"mapped-edge-arrow",stroke:"#f0ad76","stroke-width":1.65,"marker-end":"url(#warmArrow)",opacity:0});
      edgeMark.dataset.orientation=String((i+j)%2?1:-1);
    }
  }

  function buildFinal() {
    const host=$("finalLayer"),c=meshConfig;
    for(let j=0;j<5;j++)for(let i=0;i<8;i++){
      const x=c.x+i*c.dx,y=c.y+j*c.dy;
      svg("circle",{cx:x+c.dx*.5,cy:y+c.dy*.5,r:3.5,fill:"#f0ad76",opacity:.8},host);
      if((i+j)%3===0)textSvg(host,x+c.dx*.5+8,y+c.dy*.5-7,`d${j*8+i+1}`,{fill:"#f5c496","font-size":15,"font-family":"var(--math)"});
    }
  }

  function renderTheoryFocus(t){
    const focus=$("theoryFocus");
    const localFocus=ramp(t,3.06,3.2)*(1-ramp(t,3.52,3.64));
    const dofFocus=ramp(t,4.04,4.16)*(1-ramp(t,4.43,4.56));
    const basisFocus=ramp(t,5.04,5.16)*(1-ramp(t,5.43,5.56));
    const piolaFocus=ramp(t,6.04,6.16)*(1-ramp(t,6.42,6.55));
    const directionFocus=ramp(t,8.04,8.15)*(1-ramp(t,8.34,8.46));
    const globalFocus=ramp(t,9.04,9.24)*(1-ramp(t,9.76,9.98));
    const total=Math.max(localFocus,dofFocus,basisFocus,piolaFocus,directionFocus,globalFocus);
    focus.style.visibility=total>.001?"visible":"hidden";
    focus.style.opacity=String(total);
    focus.style.backgroundColor=(localFocus>.01||globalFocus>.01)?"rgba(2,13,21,.9)":"rgba(2,13,21,.84)";
    focus.setAttribute("aria-hidden",total>.001?"false":"true");

    const localIn=ramp(t,3.12,3.24)*(1-ramp(t,3.48,3.6));
    $("localTheory").style.opacity=String(localIn);
    $("localTheory").style.transform=`translate3d(0,${(28*(1-localIn)).toFixed(2)}px,0)`;
    const formulaIn=ramp(t,3.19,3.29),partsIn=ramp(t,3.27,3.37),conclusionIn=ramp(t,3.35,3.46);
    $("localTheoryFormula").style.opacity=String(formulaIn);
    $("localTheoryFormula").style.transform=`translate3d(0,${(16*(1-formulaIn)).toFixed(2)}px,0)`;
    $("localTheoryParts").style.opacity=String(partsIn);
    $("localTheoryParts").style.transform=`translate3d(0,${(14*(1-partsIn)).toFixed(2)}px,0)`;
    $("localTheoryConclusion").style.opacity=String(conclusionIn);

    const revealPanel=(id,show)=>{
      $(id).style.opacity=String(show);
      $(id).style.transform=`translate3d(0,${(24*(1-show)).toFixed(2)}px,0)`;
    };
    const reveal=(id,show,shift=12)=>{
      $(id).style.opacity=String(show);
      $(id).style.transform=`translate3d(0,${(shift*(1-show)).toFixed(2)}px,0)`;
    };

    const dofIn=ramp(t,4.1,4.21)*(1-ramp(t,4.39,4.51));
    revealPanel("dofTheory",dofIn);
    reveal("dofTheoryFormula",ramp(t,4.16,4.26));
    reveal("dofTheoryChain",ramp(t,4.22,4.32));
    reveal("dofTheoryProof",ramp(t,4.28,4.37));
    $("dofTheoryConclusion").style.opacity=String(ramp(t,4.33,4.4));

    const basisIn=ramp(t,5.1,5.21)*(1-ramp(t,5.39,5.51));
    revealPanel("basisTheory",basisIn);
    reveal("basisTheoryFormula",ramp(t,5.16,5.26));
    reveal("basisTheoryMatrix",ramp(t,5.22,5.32));
    reveal("basisTheoryRebuild",ramp(t,5.28,5.37));
    $("basisTheoryConclusion").style.opacity=String(ramp(t,5.33,5.4));

    const piolaIn=ramp(t,6.1,6.21)*(1-ramp(t,6.38,6.5));
    revealPanel("piolaTheory",piolaIn);
    reveal("piolaTheoryFormula",ramp(t,6.16,6.27));
    reveal("piolaTheoryInvariant",ramp(t,6.24,6.34));
    $("piolaTheoryConclusion").style.opacity=String(ramp(t,6.31,6.39));

    const directionIn=ramp(t,8.09,8.2)*(1-ramp(t,8.3,8.42));
    revealPanel("directionTheory",directionIn);
    reveal("directionTheoryFormula",ramp(t,8.14,8.24));
    reveal("directionTheoryBasis",ramp(t,8.2,8.29));
    $("directionTheoryConclusion").style.opacity=String(ramp(t,8.26,8.33));

    const globalIn=ramp(t,9.13,9.32)*(1-ramp(t,9.72,9.94));
    $("globalTheory").style.opacity=String(globalIn);
    $("globalTheory").style.transform=`translate3d(0,${(28*(1-globalIn)).toFixed(2)}px,0)`;
    [...$("globalTheoryFlow").children].forEach((node,index)=>{
      const show=ramp(t,9.26+index*.065,9.43+index*.065);
      node.style.opacity=String(show);
      node.style.transform=`translate3d(${((index%2?0:18)*(1-show)).toFixed(2)}px,0,0)`;
    });
    const globalConclusion=ramp(t,9.59,9.73);
    $("globalTheoryConclusion").style.opacity=String(globalConclusion);
  }

  function renderKnowledge(t) {
    scene[1].classList.toggle("is-compare",t>=4&&t<6.12);
    const field=$("globalField"),mesh=$("globalMesh"),focus=$("globalFocus"),local=$("localLayer"),compare=$("compareLayer"),assembly=$("assemblyLayer"),piola=$("piolaLayer"),stitch=$("stitchLayer"),final=$("finalLayer");
    const extraction=ramp(t,2.04,2.82),comparison=ramp(t,4.45,4.8),piolaIn=ramp(t,6.44,6.64),stitchIn=ramp(t,7.04,7.18),assemblyIn=ramp(t,8.66,8.78),finalIn=ramp(t,9.12,9.5);
    const piolaFocus=ramp(t,6.42,6.58)*(1-ramp(t,7,7.24));
    const stitchFocus=ramp(t,7.04,7.2)*(1-ramp(t,8.76,8.94));
    field.style.opacity=String(clamp((.68+.32*ramp(t,0,.4)-.48*comparison+.12*piolaIn+.13*assemblyIn)*(1-.72*piolaFocus)*(1-.78*stitchFocus)));
    mesh.style.opacity=String(clamp((ramp(t,1,1.22)-.2*comparison+.2*piolaIn+.24*assemblyIn)*(1-.88*piolaFocus)*(1-.72*stitchFocus)));
    const meshProgress=clamp(t-1);
    mesh.querySelectorAll("path").forEach(path=>{
      const depth=Number(path.dataset.depth),length=Number(path.dataset.length);
      const growthStart=Math.min(.58,depth*.2),growthEnd=Math.min(.88,growthStart+.28);
      const grown=ramp(meshProgress,growthStart,growthEnd);
      path.style.strokeDasharray=String(length);path.style.strokeDashoffset=String(length*(1-grown));
      path.style.opacity=String(.25+.75*grown);
    });
    $("knowledgeVeil").setAttribute("opacity",String(clamp(.79*ramp(t,2.12,2.62)*(1-ramp(t,6,6.25)))));
    $("globalAnnotations").style.opacity=String(clamp(ramp(t,1.64,1.88)*(1-ramp(t,2.05,2.45))));
    focus.style.opacity=String(clamp(ramp(t,2.01,2.18)*(1-ramp(t,2.62,2.94))));
    [...focus.children].forEach((node,index)=>node.style.opacity=index===0?"1":"0");
    local.style.opacity=String(clamp(ramp(t,2.04,2.28)*(1-ramp(t,4,4.5))));
    const x=lerp(394,265,extraction),y=lerp(293,122,extraction),scale=lerp(.427,1.72,extraction);
    local.setAttribute("transform",`translate(${x.toFixed(2)} ${y.toFixed(2)}) scale(${scale.toFixed(3)})`);
    $("leftLocal").setAttribute("transform","");
    $("rightLocal").setAttribute("transform","");
    $("rightLocal").style.opacity="0";
    $("sharedEdge").style.opacity="0";
    $("tangentMarks").style.opacity="0";
    const localSpace=ramp(t,3.5,3.94)*(1-ramp(t,4,4.42));
    $("leftEdgeCue").style.opacity=String(localSpace);$("rightEdgeCue").style.opacity="0";
    $("leftFieldLabel").textContent=t<3.18?"E|K":"v ∈ N₀(K)";
    $("rightFieldLabel").textContent="";
    $("leftLocalField").querySelectorAll("line").forEach(a=>{
      const x=Number(a.getAttribute("x1")),y=Number(a.getAttribute("y1"));
      const baseX=Number(a.dataset.baseX2),baseY=Number(a.dataset.baseY2);
      const swirlX=baseX-(y-110)*.055,swirlY=baseY+(x-110)*.055;
      a.setAttribute("x2",lerp(baseX,swirlX,localSpace).toFixed(2));
      a.setAttribute("y2",lerp(baseY,swirlY,localSpace).toFixed(2));
    });
    document.querySelectorAll(".local-extra").forEach(a=>a.style.opacity=String(ramp(t,2.35,2.86)*.31*(1-ramp(t,4,4.35))));
    if(state.page===1){
      const part=state.p;
      let caption=knowledge[state.stage].text,formula=knowledge[state.stage].formula;
      if(state.stage===1){caption=part<.7?"外边界先出现，三角剖分从四周向中心生长。":"网格划分区域；每个单元看到的是整体场在该处的限制。";formula=part<.7?"domain":"restriction";}
      if(state.stage===2)caption=part<.3?"整体网格仍在原位，其中一个三角形先被高亮。":part<.72?"这个单元从原位置连续放大，里面的场也随它一起展开。":"现在只研究一个单元 K，暂时不讨论与邻居怎样拼接。";
      if(state.stage===3){caption=part<.34?"局部场先保留整体电场在 K 上的限制。":part<.72?"向量逐渐显出平移与旋转两种趋势。":"最低阶局部空间控制场的变化方式，但还没有涉及公共边。";formula="localSpace";}
      if(state.stage===4)caption=part<.42?"左边在节点读取完整向量；右边沿有向边读取切向积分。":part<.78?"同一个三角形，用不同的数据方式描述局部场。":"电磁场需要切向迹与旋度结构，Nédélec 的边自由度更自然。";
      if(state.stage===5){
        const transition=state.basisTransition;
        const q=transition?ease((performance.now()-transition.begin)/transition.duration):1;
        formula=(transition&&q<.5?transition.from.mode:state.basisMode)==="node"?"lagrangeBasis":"basis";
        $("knowledgeFormula").style.opacity=transition?String(Math.max(.15,Math.abs(q-.5)*2)):"1";
      }else $("knowledgeFormula").style.opacity="1";
      if(state.stage===6)caption=part<.46?"先把参考三角形连续拉伸到一个物理三角形。":part<.78?"同一参考基函数逐个映射到整张网格。":"形状可以不同，但对应有向边的切向积分保持。";
      if(state.stage===7){caption=part<.34?"从已经完成映射的物理网格中取出两个相邻单元。":part<.78?"两个单元连续靠拢，两份公共边在几何位置上重合。":"现在仅仅是几何相邻：还没有处理局部边方向，也不能宣称切向连续。";formula="geometry";}
      if(state.stage===8){caption=part<.42?"贴合以后才看见问题：同一公共边在两个单元中可能采用相反的局部方向。":part<.66?"用符号 sₖ,ₑ 把两侧读数换算到同一全局方向，再共享同一个 dₑ。":part<.84?"最低阶切向迹在边上是常数，因此一个共享读数锁定整条边；法向仍可不同。":"同样的方向校正同时扩展到整张网格，形成统一的全局边编号。";formula=part<.58?"orientation":"tangent";}
      if($("knowledgeText").textContent!==caption)$("knowledgeText").textContent=caption;
      if($("knowledgeFormula").dataset.formula!==formula){$("knowledgeFormula").innerHTML=math[formula];$("knowledgeFormula").dataset.formula=formula;}
    }
    compare.style.opacity=String(clamp(comparison*(1-ramp(t,6,6.12))));
    $("comparisonLeft").setAttribute("transform",`translate(${lerp(295,120,comparison).toFixed(1)} 158) scale(${lerp(.76,1,comparison).toFixed(3)})`);
    $("comparisonRight").setAttribute("transform",`translate(${lerp(295,486,comparison).toFixed(1)} 158) scale(${lerp(.76,1,comparison).toFixed(3)})`);
    const transition=state.basisTransition;
    const q=transition?ease((performance.now()-transition.begin)/transition.duration):1;
    const from=transition?.from||{mode:state.basisMode,node:state.basisNode,component:state.basisComponent,edge:state.basisEdge};
    const nodeChanged=from.node!==state.basisNode||from.component!==state.basisComponent;
    const edgeChanged=from.edge!==state.basisEdge;
    const nodeQ=nodeChanged?q:1,edgeQ=edgeChanged?q:1;
    const basisOpacity=ramp(t,5.45,5.86);
    $("compareNodeBasis").style.opacity=String(basisOpacity*nodeQ);
    $("compareNodeBasisGhost").style.opacity=String(basisOpacity*(1-nodeQ));
    $("compareEdgeBasis").style.opacity=String(basisOpacity*edgeQ);
    $("compareEdgeBasisGhost").style.opacity=String(basisOpacity*(1-edgeQ));
    $("compareNodeInfo").style.opacity=String(clamp(1-ramp(t,5.45,5.86)*.55));
    $("compareEdgeInfo").style.opacity=String(clamp(1-ramp(t,5.45,5.86)*.55));
    const paintNode=(id,node,component)=>$(id).querySelectorAll("line").forEach(a=>{
      const x=Number(a.dataset.x),y=Number(a.dataset.y),lb=(x-20)/290,lc=(y-28)/264;
      const weight=[1-lb-lc,lb,lc][node]*22;
      a.setAttribute("x2",(x+(component===0?weight:0)).toFixed(2));
      a.setAttribute("y2",(y+(component===1?weight:0)).toFixed(2));
    });
    const paintEdge=(id,edge)=>$(id).querySelectorAll("line").forEach(a=>{
      const x=Number(a.dataset.x),y=Number(a.dataset.y),lb=(x-20)/290,lc=(y-28)/264,la=1-lb-lc;
      const vectors=[[(la+lb)/290,lb/264],[-lc/290,lb/264],[-lc/290,-(lc+la)/264]];
      const [u,v]=vectors[edge];
      a.setAttribute("x2",(x+u*5200).toFixed(2));a.setAttribute("y2",(y+v*5200).toFixed(2));
    });
    paintNode("compareNodeBasis",state.basisNode,state.basisComponent);
    paintNode("compareNodeBasisGhost",from.node,from.component);
    paintEdge("compareEdgeBasis",state.basisEdge);
    paintEdge("compareEdgeBasisGhost",from.edge);
    if(from.nodeVectors)$("compareNodeBasisGhost").querySelectorAll("line").forEach((line,i)=>{
      line.setAttribute("x2",from.nodeVectors[i][0]);line.setAttribute("y2",from.nodeVectors[i][1]);
    });
    if(from.edgeVectors)$("compareEdgeBasisGhost").querySelectorAll("line").forEach((line,i)=>{
      line.setAttribute("x2",from.edgeVectors[i][0]);line.setAttribute("y2",from.edgeVectors[i][1]);
    });
    const localOnly=ramp(t,5.45,5.84);
    $("leftLowerTri").style.opacity=String(1-localOnly*.83);$("rightLowerTri").style.opacity=String(1-localOnly*.83);
    $("leftNormalComparison").style.opacity=String(1-localOnly);
    $("rightNormalComparison").style.opacity=String(1-localOnly);
    $("leftNormalB").setAttribute("x2",String(lerp(214,198,ramp(t,4.2,4.85))));
    $("leftNormalB").setAttribute("y2",String(lerp(166,150,ramp(t,4.2,4.85))));
    const selectedNode=[[20,28],[310,28],[20,292]][state.basisNode];
    const oldNode=from.nodeMarker||[[20,28],[310,28],[20,292]][from.node];
    $("selectedBasisNode").setAttribute("cx",lerp(oldNode[0],selectedNode[0],nodeQ));$("selectedBasisNode").setAttribute("cy",lerp(oldNode[1],selectedNode[1],nodeQ));
    $("selectedBasisNodeGhost").setAttribute("cx",oldNode[0]);$("selectedBasisNodeGhost").setAttribute("cy",oldNode[1]);
    $("compareNodeRead").textContent=`节点 ${state.basisNode+1}：${state.basisComponent?"y":"x"} 分量 = 1；其余 = 0`;
    $("compareNodeReadGhost").textContent=`节点 ${from.node+1}：${from.component?"y":"x"} 分量 = 1；其余 = 0`;
    $("selectedBasisEdge").setAttribute("d",["M20 28 H310","M310 28 L20 292","M20 292 V28"][state.basisEdge]);
    $("selectedBasisEdgeGhost").setAttribute("d",from.edgePath||["M20 28 H310","M310 28 L20 292","M20 292 V28"][from.edge]);
    $("compareEdgeRead").textContent=["d₁₂ = 1   d₂₃ = 0   d₃₁ = 0","d₁₂ = 0   d₂₃ = 1   d₃₁ = 0","d₁₂ = 0   d₂₃ = 0   d₃₁ = 1"][state.basisEdge];
    $("compareEdgeReadGhost").textContent=["d₁₂ = 1   d₂₃ = 0   d₃₁ = 0","d₁₂ = 0   d₂₃ = 1   d₃₁ = 0","d₁₂ = 0   d₂₃ = 0   d₃₁ = 1"][from.edge];
    for(const id of ["selectedBasisNode","compareNodeRead"])$(id).style.opacity=String(localOnly*nodeQ);
    for(const id of ["selectedBasisNodeGhost","compareNodeReadGhost"])$(id).style.opacity=String(localOnly*(1-nodeQ));
    for(const id of ["selectedBasisEdge","compareEdgeRead"])$(id).style.opacity=String(localOnly*edgeQ);
    for(const id of ["selectedBasisEdgeGhost","compareEdgeReadGhost"])$(id).style.opacity=String(localOnly*(1-edgeQ));
    assembly.style.opacity=String(clamp(assemblyIn*(1-ramp(t,9.02,9.2))));
    $("assemblyPair").style.opacity="0";
    $("pairGlobalArrow").style.transform=`rotate(${state.reverse?180:0}deg)`;
    $("pairDirectionRead").textContent=state.reverse?"−  与  +  →  同一全局 dₑ":"+  与  −  →  同一全局 dₑ";
    assembly.querySelectorAll("[data-wave]").forEach(g=>{
      const wave=Number(g.dataset.wave), show=ramp(t,8.66+wave*.014,8.78+wave*.014);
      g.style.opacity=String(show);
      g.style.filter=show>.05&&show<.94?"drop-shadow(0 0 5px #f0ad76)":"none";
      const edge=g.querySelector("line"),merge=ramp(t,8.78+wave*.008,8.86+wave*.008),x=Number(g.dataset.x),y=Number(g.dataset.y);
      g.setAttribute("transform",`translate(${((430-x)*(1-show)).toFixed(2)} ${((270-y)*(1-show)).toFixed(2)})`);
      edge.style.transform=`rotate(${state.reverse?180:0}deg)`;
      edge.style.opacity=String(1-.8*merge);
      const sign=Number(g.dataset.sign)*(state.reverse?-1:1);
      const signText=g.querySelector("text");signText.textContent=sign>0?"+":"−";
      signText.setAttribute("x",String(lerp(x+19,x+2,merge)));
      signText.style.opacity=String(1-merge);
      g.querySelector(".global-edge-dot").setAttribute("opacity",String(merge));
      g.querySelector(".global-edge-id").setAttribute("opacity",String(merge));
    });
    piola.style.opacity=String(clamp(piolaIn*(1-ramp(t,7.02,7.18))));
    const many=ramp(t,6.62,6.78),one=1-ramp(t,6.62,6.78);
    $("piolaOne").style.opacity=String(clamp(one));
    $("piolaMany").style.opacity=String(clamp(many));
    const mapOne=ramp(t,6.44,6.74);
    const refVertices=[[100,490],[315,490],[100,230]],physVertices=[[420,490],[700,490],[545+state.skew,218]];
    const mappedVertices=refVertices.map((point,index)=>[lerp(point[0],physVertices[index][0],mapOne),lerp(point[1],physVertices[index][1],mapOne)]);
    $("piolaPhysicalTriangle").setAttribute("d",`M${mappedVertices[0][0]} ${mappedVertices[0][1]} L${mappedVertices[1][0]} ${mappedVertices[1][1]} L${mappedVertices[2][0]} ${mappedVertices[2][1]} Z`);
    const a=280/215,b=-(125+state.skew)/260,d=272/260;
    $("piolaPhysicalField").querySelectorAll("line").forEach(edge=>{
      const r=Number(edge.dataset.r),s=Number(edge.dataset.s),refX=100+215*r,refY=490-260*s,targetX=420+280*r+(125+state.skew)*s,targetY=490-272*s,x=lerp(refX,targetX,mapOne),y=lerp(refY,targetY,mapOne);
      const u=14+5*Math.sin(4*s+2*r),v=-8+4*Math.cos(3*r),tx=u/a,ty=-b*u/(a*d)+v/d;
      edge.setAttribute("x1",x.toFixed(2));edge.setAttribute("y1",y.toFixed(2));
      edge.setAttribute("x2",(x+lerp(u,tx,mapOne)).toFixed(2));edge.setAttribute("y2",(y+lerp(v,ty,mapOne)).toFixed(2));
      edge.style.opacity=String(ramp(t,6.5,6.7));
    });
    $("piolaMany").querySelectorAll("[data-wave]").forEach(g=>{
      const wave=Number(g.dataset.wave),show=ramp(t,6.6+wave*.012,6.72+wave*.012),x=Number(g.dataset.x),y=Number(g.dataset.y);
      g.style.opacity=String(show);
      g.setAttribute("transform",`translate(${((555-x)*(1-show)).toFixed(2)} ${((355-y)*(1-show)).toFixed(2)})`);
      g.querySelector(".mapped-edge-arrow").setAttribute("opacity",String(ramp(t,6.72+wave*.008,6.84+wave*.008)));
    });
    const stitchOut=1-ramp(t,8.82,8.94),join=ramp(t,7.46,7.72);
    stitch.style.opacity=String(clamp(stitchIn*stitchOut));
    $("stitchLeftCell").setAttribute("transform",`translate(${lerp(80,210,join).toFixed(2)} 160)`);
    $("stitchRightCell").setAttribute("transform",`translate(${lerp(560,430,join).toFixed(2)} 160)`);
    $("stitchGeometryNote").style.opacity=String(ramp(t,7.74,7.86)*(1-ramp(t,8.02,8.16)));
    $("stitchLocalDirections").style.opacity=String(ramp(t,8.46,8.56)*(1-ramp(t,8.64,8.74)));
    $("stitchDirectionSigns").style.opacity=String(ramp(t,8.52,8.64)*(1-ramp(t,8.72,8.82)));
    $("stitchGlobalArrow").style.transform=`rotate(${state.reverse?180:0}deg)`;
    $("stitchLeftSign").textContent=state.reverse?"sₖ₁,ₑ = −1":"sₖ₁,ₑ = +1";
    $("stitchRightSign").textContent=state.reverse?"sₖ₂,ₑ = +1":"sₖ₂,ₑ = −1";
    $("stitchTangents").style.opacity=String(ramp(t,8.58,8.7));
    $("stitchLeftTangents").setAttribute("transform",`translate(${(130*join).toFixed(2)} 0)`);
    $("stitchRightTangents").setAttribute("transform",`translate(${(-140*join).toFixed(2)} 0)`);
    $("stitchNormals").style.opacity=String(ramp(t,8.62,8.72)*(1-.18*join));
    $("stitchLeftNormal").setAttribute("transform",`translate(${(130*join).toFixed(2)} 0)`);
    $("stitchRightNormal").setAttribute("transform",`translate(${(-140*join).toFixed(2)} 0)`);
    $("stitchLock").style.opacity=String(ramp(t,8.56,8.68));
    $("stitchStatement").style.opacity=String(ramp(t,8.68,8.78));
    final.style.opacity=String(finalIn);
    renderTheoryFocus(t);
  }

  function buildImplementationMesh() {
    const host=$("implMesh");
    for(let j=0;j<=6;j++)for(let i=0;i<=8;i++){
      const x=62+i*83,y=112+j*68;
      const add=(d,length,depth)=>svg("path",{d,"data-length":length.toFixed(2),"data-depth":depth.toFixed(2)},host);
      if(i<8)add(`M${x} ${y} H${x+83}`,83,Math.min(i+.5,7.5-i,j,6-j));
      if(j<6)add(`M${x} ${y} V${y+68}`,68,Math.min(i,8-i,j+.5,5.5-j));
      if(i<8&&j<6)add(`M${x} ${y+68} L${x+83} ${y}`,Math.hypot(83,68),Math.min(i+.5,7.5-i,j+.5,5.5-j));
    }
  }
  const chartData={n:[4,8,16,32],dofs:[56,208,800,3136]};
  // Keep the live SVG nodes between frames. Replacing the whole fragment on
  // every tick turns a continuous change into a succession of new pictures.
  function reconcileSvg(host,fragment){
    const incoming=[...fragment.childNodes],existing=[...host.childNodes];
    incoming.forEach((fresh,i)=>{
      const live=existing[i];
      if(!live||live.nodeName!==fresh.nodeName){
        host.insertBefore(fresh,live||null);
        if(live)live.remove();
        return;
      }
      for(const attr of [...live.attributes])if(!fresh.hasAttribute(attr.name))live.removeAttribute(attr.name);
      for(const attr of [...fresh.attributes])if(live.getAttribute(attr.name)!==attr.value)live.setAttribute(attr.name,attr.value);
      if(live.nodeName==="text"&&live.textContent!==fresh.textContent)live.textContent=fresh.textContent;
    });
    for(let i=incoming.length;i<existing.length;i++)existing[i].remove();
  }
  function renderImplementation(step,p) {
    const mesh=$("implMesh"),overlayHost=$("implOverlay"),chartHost=$("implChart"),field=$("implField");
    const overlay=document.createDocumentFragment(),chart=document.createDocumentFragment();
    const vis=ramp(p,.02,.86);
    const stageEntry=ramp(p,0,.24),stageScale=.92+.08*stageEntry;
    const stageShift=28*(1-stageEntry);
    overlayHost.setAttribute("transform",`translate(${(400*(1-stageScale)).toFixed(2)} ${(320*(1-stageScale)+stageShift).toFixed(2)}) scale(${stageScale.toFixed(4)})`);
    overlayHost.setAttribute("opacity",String(stageEntry));
    chartHost.setAttribute("transform",`translate(${(400*(1-stageScale)).toFixed(2)} ${(320*(1-stageScale)+stageShift).toFixed(2)}) scale(${stageScale.toFixed(4)})`);
    chartHost.setAttribute("opacity",String(stageEntry));
    // Position is part of the timeline, not a CSS after-effect: the first
    // frame and a manually scrubbed frame therefore have the same geometry.
    const fieldEntry=ramp(p,0,.72),meshEntry=ramp(p,0,.82);
    field.setAttribute("transform",step===0?`translate(${(-54*(1-fieldEntry)).toFixed(2)} 0)`:"");
    mesh.setAttribute("transform",step===1?`translate(${(400*(1-(.88+.12*meshEntry))).toFixed(2)} ${(316*(1-(.88+.12*meshEntry))).toFixed(2)}) scale(${(.88+.12*meshEntry).toFixed(4)})`:"");
    mesh.style.opacity=String(step===7?.06:step===3?.07:step===4?.23:step===0?0:step===1?lerp(.12,.9,vis):step===5?.4:.5);
    field.style.opacity=String(step===0?lerp(.08,.95,vis):step===6?lerp(.22,.78,vis):[0,.48,.32,.11,.14,.2,0,0][step]);
    if(step===1||state.implMeshWasGrowing){
      mesh.querySelectorAll("path").forEach(path=>{
        const length=Number(path.dataset.length),depth=Number(path.dataset.depth);
        const growth=step===1?ramp(p,.03+depth*.1,.43+depth*.1):1;
        path.style.strokeDasharray=String(length);path.style.strokeDashoffset=String(length*(1-growth));
      });
    }
    state.implMeshWasGrowing=step===1;
    $("implFieldA").style.opacity=state.model==="A"?"1":"0";
    $("implFieldB").style.opacity=state.model==="B"?"1":"0";
    const model=examples[state.model];
    if(step===0||step===6){
      if(step===6){
        for(let j=0;j<6;j++)for(let i=0;i<8;i++){
          const x=62+i*83+41.5,y=112+j*68+34;
          const show=ramp(p,.13+(i+j)*.018,.49+(i+j)*.018);
          svg("circle",{cx:lerp(x-18,x,show),cy:lerp(y+12,y,show),r:3.4*show,fill:"#f0ad76",opacity:show*.85},overlay);
        }
      }
      textSvg(overlay,76,585,step===0?"已知解析电场  E":"蓝色：解析场参照  ·  橙色：边自由度重建示意（非程序输出）",{fill:"#dbece8","font-size":step===0?20:15,"font-family":"var(--math)",opacity:vis});
    } else if(step===1){
      svg("rect",{x:62,y:112,width:664,height:408,fill:"rgba(65,154,165,.06)",stroke:"#e6b478","stroke-width":2,opacity:vis},overlay);
      textSvg(overlay,77,583,"三角形网格  ·  顶点  ·  边  ·  边界",{fill:"#d5e8e5","font-size":18,opacity:vis});
    } else if(step===2){
      for(let j=0;j<6;j++)for(let i=0;i<8;i++)if((i+j)%2===0){
        const x=62+i*83,y=112+j*68;
        [[x+41.5,y,0],[x,y+34,1],[x+41.5,y+34,2]].forEach(([mx,my,type],k)=>{
          const wave=(i+j)*.023;
          const show=ramp(p,.06+wave+k*.055,.39+wave+k*.055);
          const [sx,sy]=type===0?[x,y]:type===1?[x,y]:[x+83,y];
          const px=lerp(sx,mx,show),py=lerp(sy,my,show);
          svg("circle",{cx:px,cy:py,r:(type===2?4.2:3.2)*show,fill:type===2?"#f0ad76":"#6bc9ca",opacity:show*.9},overlay);
          if(type===2)line(overlay,px-10*show,py+9*show,px+10*show,py-9*show,{stroke:"#f0ad76","stroke-width":1.7,"marker-end":"url(#implArrow)",opacity:show});
          if(type===2&&i%3===0)textSvg(overlay,px+10,py-10,`d${j*8+i+1}`,{fill:"#f7c69e","font-size":13,opacity:show});
        });
      }
      textSvg(overlay,78,584,"最低阶：一条全局边 ↔ 一个切向自由度",{fill:"#d6eae6","font-size":18,opacity:vis});
    } else if(step===3){
      const matrices=[[100,"C","#75b9df"],[325,"M","#72d5c0"],[550,"A","#f0ad76"]];
      matrices.forEach(([targetX,label,color],index)=>{
        const visible=index===2?ramp(p,.48,.9):ramp(p,.04,.37);
        const sx=targetX+(index===0?-88:96)*(1-visible);
        textSvg(overlay,sx+53,154,label,{fill:color,"font-size":28,"font-family":"var(--math)",opacity:visible});
        svg("rect",{x:sx,y:178,width:156,height:185,rx:3,fill:"rgba(13,49,62,.35)",stroke:color,"stroke-width":1,opacity:visible*.8},overlay);
        for(let r=0;r<10;r++)for(let c=0;c<8;c++)if(r===c||(r+c+index)%4===0||(index===2&&Math.abs(r-c)<2)){
          const start=(index===2?.44:.1)+(r+c)*.012;
          const cell=ramp(p,start,start+.22);
          svg("rect",{x:sx+12+c*18,y:192+r*16,width:4.5,height:4.5,rx:1,fill:color,opacity:visible*cell*.8},overlay);
        }
      });
      textSvg(overlay,280,289,state.model==="A"?"+":"−k²",{fill:"#e8e1c9","font-size":30,"font-family":"var(--math)",opacity:vis});
      svg("path",{d:"M490 273 H535",stroke:"#f0ad76","stroke-width":2,"marker-end":"url(#implArrow)",opacity:ramp(p,.35,.7)},overlay);
      textSvg(overlay,230,493,state.model==="A"?"旋度矩阵 + 质量矩阵":"旋度矩阵 − k² × 质量矩阵",{fill:"#d7e9e2","font-size":20,opacity:vis});
      textSvg(overlay,263,548,state.model==="A"?"A = C + M":"A = C − k²M",{fill:"#e6f4e9","font-size":28,"font-family":"var(--math)",opacity:ramp(p,.55,.9)});
    } else if(step===4){
      for(let j=0;j<5;j++)for(let i=0;i<7;i++){
        const x=115+i*84,y=145+j*78;
        const show=ramp(p,.07+(i+j)*.035,.42+(i+j)*.035);
        line(overlay,x,y,x+21*show,y+16*show,{stroke:"#e6b478","stroke-width":2,"marker-end":"url(#implArrow)",opacity:show*.8});
      }
      textSvg(overlay,92,585,"连续源项  →  离散右端向量 b",{fill:"#e5ebe1","font-size":19,opacity:vis});
    } else if(step===5){
      svg("rect",{x:62,y:112,width:664,height:408,fill:"none",stroke:"#f0ad76","stroke-width":5,"stroke-dasharray":2144,"stroke-dashoffset":2144*(1-vis),opacity:vis},overlay);
      for(let i=0;i<10;i++){
        const x=90+i*62,y=137+i*39;
        const show=ramp(p,.08+i*.055,.42+i*.055);
        line(overlay,x,112,x+13*show,112,{stroke:"#f7bd8c","stroke-width":1.8,"marker-end":"url(#implArrow)",opacity:show});
        line(overlay,x,520,x-13*show,520,{stroke:"#f7bd8c","stroke-width":1.8,"marker-end":"url(#implArrow)",opacity:show});
        if(i<9){line(overlay,62,y,62,y-13*show,{stroke:"#f7bd8c","stroke-width":1.8,"marker-end":"url(#implArrow)",opacity:show});line(overlay,726,y,726,y+13*show,{stroke:"#f7bd8c","stroke-width":1.8,"marker-end":"url(#implArrow)",opacity:show});}
      }
      textSvg(overlay,248,325,"只取边界切向读数",{fill:"#f2c19a","font-size":25,opacity:vis});
      textSvg(overlay,81,584,state.model==="A"?"边界切向自由度 = 0":"边界切向自由度 = 解析场的边积分",{fill:"#e5ebe1","font-size":18,opacity:vis});
    } else if(step===7){
      const left=80,right=720,top=94,bottom=475;
      const axes=ramp(p,0,.24);
      svg("path",{d:`M${left} ${top} V${bottom} H${right}`,stroke:"#80abb4","stroke-width":2,"stroke-dasharray":1021,"stroke-dashoffset":1021*(1-axes),opacity:axes},chart);
      const yFor=value=>top+18+Math.log(.5/value)/Math.log(.5/1e-5)*(bottom-top-35);
      [.1,.01,.001,.0001].forEach(value=>{
        const y=yFor(value);line(chart,left,y,left+(right-left)*axes,y,{stroke:"#557884","stroke-width":.8,opacity:.45*axes});
        textSvg(chart,left-10,y+5,String(value),{"text-anchor":"end",fill:"#8cabb1","font-size":12,"font-family":"var(--math)",opacity:axes});
      });
      const draw=(values,color)=>{
        const pts=values.map((v,i)=>[left+55+i*183,yFor(v)]);
        const plotProgress=ramp(p,.08,.88),position=plotProgress*3,index=Math.min(2,Math.floor(position)),fraction=position-index;
        const visible=pts.slice(0,index+1);
        if(position>0&&position<3)visible.push([lerp(pts[index][0],pts[index+1][0],fraction),lerp(pts[index][1],pts[index+1][1],fraction)]);
        if(position>=3)visible.push(pts[3]);
        svg("polyline",{points:visible.map(a=>a.join(",")).join(" "),stroke:color,"stroke-width":3.4,fill:"none",opacity:.95},chart);
        pts.forEach((a,i)=>{const show=i===0?axes:ramp(plotProgress,(i-1)/3,i/3);svg("circle",{cx:a[0],cy:a[1],r:5*show,fill:color,opacity:show},chart);textSvg(chart,a[0],bottom+28,String(chartData.n[i]),{"text-anchor":"middle",fill:"#adcccf","font-size":16,opacity:axes});});
      };
      draw(model.errors,"#76b9dd");draw(model.curls,"#71d6be");
      const samplePosition=ramp(p,.08,.88)*3,active=Math.min(3,Math.floor(samplePosition+1e-6));
      const changeDistance=Math.min(Math.abs(samplePosition-1),Math.abs(samplePosition-2));
      const readoutOpacity=axes*ramp(changeDistance,0,.08);
      textSvg(chart,120,563,`n = ${chartData.n[active]}   ·   全局边自由度 ${chartData.dofs[active]}`,{fill:"#dbe8e5","font-size":18,opacity:readoutOpacity});
      textSvg(chart,120,593,`场误差 ${model.errors[active].toExponential(3)}   ·   旋度误差 ${model.curls[active].toExponential(3)}`,{fill:"#a7c6c9","font-size":16,"font-family":"var(--math)",opacity:readoutOpacity});
      textSvg(chart,104,58,"● 场误差",{fill:"#76b9dd","font-size":17,opacity:axes});textSvg(chart,278,58,"● 旋度误差",{fill:"#71d6be","font-size":17,opacity:axes});
    }
    reconcileSvg(overlayHost,overlay);reconcileSvg(chartHost,chart);
  }

  function currentStages(){return state.page===1?knowledge:implementation;}
  function renderCaption(){
    if(state.page===1){
      const d=knowledge[state.stage];
      $("knowledgeIndex").textContent=`${String(state.stage+1).padStart(2,"0")} / ${String(knowledge.length).padStart(2,"0")}`;
      $("knowledgeKicker").textContent=d.name;$("knowledgeTitle").textContent=d.title;$("knowledgeText").textContent=d.text;
      $("knowledgeFormula").innerHTML=math[d.formula];
      renderExtras();
    }else if(state.page===2){
      const d=implementation[state.stage],model=examples[state.model];
      $("implementationIndex").textContent=`${String(state.stage+1).padStart(2,"0")} / ${String(implementation.length).padStart(2,"0")}`;
      $("implementationTitle").textContent=d.title;$("implementationText").textContent=d.text;
      $("implementationFormula").innerHTML=math[d.formula(state.model)];
      $("implementationCode").textContent=d.code(state.model);
      $("modelNote").textContent=`${model.file} · ${model.note}`;
      $("visualFootnote").textContent=state.stage===7?"数据来自本项目编程教学文档；两模型使用不同制造解，误差数值不作横向排名。":d.text;
      document.querySelectorAll("[data-model]").forEach(b=>b.classList.toggle("active",b.dataset.model===state.model));
    }
  }

  function renderExtras(){
    const host=$("knowledgeExtras");host.innerHTML="";
    if(state.stage===5){
      [["节点 1","node",0],["节点 2","node",1],["节点 3","node",2],["x 分量","component",0],["y 分量","component",1],["边 12","edge",0],["边 23","edge",1],["边 31","edge",2]].forEach(([label,mode,value])=>{
        const b=document.createElement("button");b.type="button";b.textContent=label;
        b.classList.toggle("active",mode==="node"?state.basisMode==="node"&&state.basisNode===value:mode==="component"?state.basisMode==="node"&&state.basisComponent===value:state.basisMode==="edge"&&state.basisEdge===value);
        b.addEventListener("click",()=>{
          if(mode==="node"&&state.basisMode==="node"&&state.basisNode===value||mode==="component"&&state.basisMode==="node"&&state.basisComponent===value||mode==="edge"&&state.basisMode==="edge"&&state.basisEdge===value)return;
          const from={mode:state.basisMode,node:state.basisNode,component:state.basisComponent,edge:state.basisEdge};
          const snapshotVectors=(activeId,ghostId)=>{
            const active=$(activeId),ghost=$(ghostId),aOpacity=Number(active.style.opacity||0),gOpacity=Number(ghost.style.opacity||0),wa=aOpacity+gOpacity<.01?1:aOpacity,wg=aOpacity+gOpacity<.01?0:gOpacity,sum=wa+wg;
            const current=active.querySelectorAll("line"),previous=ghost.querySelectorAll("line");
            return [...current].map((line,i)=>["x2","y2"].map(attr=>((Number(line.getAttribute(attr))*wa+Number(previous[i].getAttribute(attr))*wg)/sum).toFixed(2)));
          };
          const snapshotMarker=(activeId,ghostId)=>{
            const a=$(activeId),g=$(ghostId),aOpacity=Number(a.style.opacity||0),gOpacity=Number(g.style.opacity||0),wa=aOpacity+gOpacity<.01?1:aOpacity,wg=aOpacity+gOpacity<.01?0:gOpacity,sum=wa+wg;
            return ["cx","cy"].map(attr=>(Number(a.getAttribute(attr))*wa+Number(g.getAttribute(attr))*wg)/sum);
          };
          from.nodeVectors=snapshotVectors("compareNodeBasis","compareNodeBasisGhost");
          from.edgeVectors=snapshotVectors("compareEdgeBasis","compareEdgeBasisGhost");
          from.nodeMarker=snapshotMarker("selectedBasisNode","selectedBasisNodeGhost");
          from.edgePath=Number($("selectedBasisEdge").style.opacity||0)>=Number($("selectedBasisEdgeGhost").style.opacity||0)
            ?$("selectedBasisEdge").getAttribute("d"):$("selectedBasisEdgeGhost").getAttribute("d");
          if(mode==="node"){state.basisMode="node";state.basisNode=value;}
          else if(mode==="component"){state.basisMode="node";state.basisComponent=value;}
          else{state.basisMode="edge";state.basisEdge=value;}
          if(!reduced.matches){
            const transition={from,begin:performance.now(),duration:620};
            state.basisTransition=transition;
            scene[1].classList.add("is-basis-changing");
            requestAnimationFrame(function animateBasis(now){
              if(state.basisTransition!==transition)return;
              renderKnowledge(state.stage+state.p);
              if(now-transition.begin<transition.duration)requestAnimationFrame(animateBasis);
              else{state.basisTransition=null;scene[1].classList.remove("is-basis-changing");renderKnowledge(state.stage+state.p);}
            });
          }else state.basisTransition=null;
          renderCaption();renderKnowledge(state.stage+state.p);
        });host.appendChild(b);
      });
    }else if(state.stage===6){
      const wrap=document.createElement("label");wrap.textContent="物理单元倾斜";
      const input=document.createElement("input");input.type="range";input.min="-90";input.max="90";input.value=state.skew;input.setAttribute("aria-label","物理单元倾斜");
      input.addEventListener("input",()=>{state.skew=Number(input.value);renderKnowledge(state.stage+state.p);});wrap.appendChild(input);host.appendChild(wrap);
    }else if(state.stage===8){
      const b=document.createElement("button");b.type="button";b.textContent="反转全局方向";
      b.addEventListener("click",()=>{state.reverse=!state.reverse;renderKnowledge(state.stage+state.p);});host.appendChild(b);
    }
  }

  function updateTransport(){
    const stages=currentStages();
    $("transportPage").textContent=state.page===1?"知识":"FEALPy";
    $("transportStage").textContent=stages[state.stage].name;
    $("transportCount").textContent=`${state.stage+1} / ${stages.length}`;
    $("timeline").value=String(Math.round(state.p*1000));
    $("timeline").style.background=`linear-gradient(90deg,#f0ad76 ${state.p*100}%,rgba(127,177,183,.34) ${state.p*100}%)`;
    $("timeline").setAttribute("aria-valuetext",`${stages[state.stage].name}，进度 ${Math.round(state.p*100)}%`);
    $("playPause").textContent=state.playing?"Ⅱ":"▶";
    $("playPause").setAttribute("aria-label",state.playing?"暂停本段":"播放本段");
    $("ambientToggle").classList.toggle("is-paused",state.ambientPaused);
    $("ambientToggle").setAttribute("aria-label",state.ambientPaused?"恢复场线流动":"暂停场线流动");
    $("previousStage").disabled=state.requestedStage===0;
    $("nextStage").disabled=state.requestedStage===stages.length-1;
    $("previousPage").disabled=state.page<=0;
    $("nextPage").disabled=state.page>=scene.length-1;
    let activeStageButton=null;
    [...stageList.children].forEach((b,i)=>{
      const active=i===state.requestedStage;
      b.classList.toggle("active",active);
      if(active){b.setAttribute("aria-current","step");activeStageButton=b;}else b.removeAttribute("aria-current");
    });
    const indicator=`${state.page}:${state.requestedStage}`;
    if(indicator!==lastStageIndicator&&activeStageButton){
      lastStageIndicator=indicator;
      activeStageButton.scrollIntoView({behavior:reduced.matches?"auto":"smooth",block:"nearest",inline:"center"});
    }
  }
  function render(){
    if(state.page===1)renderKnowledge(state.stage+state.p);
    else if(state.page===2)renderImplementation(state.stage,state.p);
    if(state.page!==0)updateTransport();
  }
  function buildStageList(){
    stageList.innerHTML="";
    currentStages().forEach((d,i)=>{const b=document.createElement("button");b.type="button";b.textContent=d.name;b.addEventListener("click",()=>seekStage(i,0));stageList.appendChild(b);});
  }
  function syncAmbient(){
    for(const page of [1,2])scene[page].classList.toggle("is-ambient",state.page===page&&!state.ambientPaused);
  }
  function stop(){state.playing=false;state.last=0;scene[1].classList.remove("is-playing");scene[2].classList.remove("is-playing");syncAmbient();updateTransport();}
  function clearImplementationFade(){
    for(const id of ["implOverlay","implChart"])$(id).style.opacity="";
    document.querySelector(".implementation-content").style.opacity="";
    $("implLeaving").replaceChildren();$("implLeaving").style.opacity="";
    scene[2].classList.remove("is-stage-transitioning");
  }
  function clearKnowledgeFade(){
    const stageRoot=document.querySelector(".knowledge-stage");
    stageRoot.style.opacity="";
    stageRoot.style.transform="";
    stageRoot.style.transformOrigin="";
    $("knowledgeSvg").style.opacity="";
    $("knowledgeSvg").style.transform="";
    $("knowledgeSvg").style.transformOrigin="";
    document.querySelector(".scene-caption").style.opacity="";
    document.querySelector(".scene-caption").style.transform="";
    document.querySelector(".scene-caption").style.transformOrigin="";
    scene[1].classList.remove("is-stage-transitioning");
  }
  function seekStage(index,p=0){
    if(state.page===0)return;
    stop();
    state.playAfterSeek=false;
    state.basisTransition=null;scene[1].classList.remove("is-basis-changing");
    const target=clamp(index,0,currentStages().length-1),startStage=state.stage,startP=state.p;
    state.requestedStage=target;
    if(reduced.matches){state.seeking=null;clearKnowledgeFade();clearImplementationFade();state.stage=target;state.p=p;renderCaption();render();return;}
    if(state.page===1&&target!==startStage&&Math.abs(startStage+startP-(target+p))<.001){
      state.seeking=null;state.stage=target;state.p=p;renderCaption();render();return;
    }
    if(state.page===1&&target!==startStage){
      clearKnowledgeFade();
      const begin=performance.now(),duration=620,stageRoot=document.querySelector(".knowledge-stage");
      const transition={kind:"knowledge",begin,target,p,duration,switched:false};
      state.seeking=transition;scene[1].classList.add("is-stage-transitioning");
      stageRoot.style.transformOrigin="43% 45%";
      requestAnimationFrame(function frame(now){
        if(state.seeking!==transition)return;
        const q=clamp((now-begin)/duration),outEnd=.44;
        if(q>=outEnd&&!transition.switched){
          transition.switched=true;state.stage=target;state.p=p;renderCaption();render();
        }
        const visibility=q<outEnd?1-ease(q/outEnd):ease((q-outEnd)/(1-outEnd));
        stageRoot.style.opacity=String(visibility);
        stageRoot.style.transform=`scale(${(.985+.015*visibility).toFixed(4)})`;
        if(q<1)requestAnimationFrame(frame);
        else{
          state.seeking=null;clearKnowledgeFade();render();
          if(state.playAfterSeek){state.playAfterSeek=false;play();}
        }
      });
      return;
    }
    if(state.page===2&&(target!==startStage||state.seeking)){
      const begin=performance.now(),duration=760;
      const panel=document.querySelector(".implementation-content"),field=$("implField"),mesh=$("implMesh"),overlay=$("implOverlay"),chart=$("implChart"),leaving=$("implLeaving");
      scene[2].classList.add("is-stage-transitioning");
      const remnants=[...leaving.children].map(child=>child.cloneNode(true));
      const remnantOpacity=Number(leaving.style.opacity||0),fieldOpacity=Number(field.style.opacity||1),meshOpacity=Number(mesh.style.opacity||1),overlayOpacity=Number(overlay.style.opacity||1),chartOpacity=Number(chart.style.opacity||1),panelOpacity=Number(panel.style.opacity||1);
      leaving.replaceChildren();
      if(remnants.length){const group=svg("g",{opacity:remnantOpacity},leaving);remnants.forEach(child=>group.appendChild(child));}
      for(const [source,opacity] of [[field,fieldOpacity],[mesh,meshOpacity],[overlay,overlayOpacity],[chart,chartOpacity]]){
        if(!source.childNodes.length)continue;
        const old=source.cloneNode(true);old.removeAttribute("id");old.querySelectorAll("[id]").forEach(node=>node.removeAttribute("id"));old.setAttribute("class",source===field?"impl-field-ghost":source===mesh?"impl-mesh-ghost":source===chart?"impl-chart-ghost":"impl-overlay-ghost");old.style.opacity="";old.setAttribute("opacity",String(opacity));leaving.appendChild(old);
      }
      leaving.style.opacity="1";
      state.stage=target;state.p=0;render();
      const targetFieldOpacity=Number(field.style.opacity||0),targetMeshOpacity=Number(mesh.style.opacity||0);
      const targetOverlayOpacity=Number(overlay.getAttribute("opacity")||0),targetChartOpacity=Number(chart.getAttribute("opacity")||0);
      field.style.opacity="0";mesh.style.opacity="0";overlay.style.opacity="0";chart.style.opacity="0";
      const transition={begin,target,p,duration,captionSwitched:false};state.seeking=transition;
      requestAnimationFrame(function frame(now){
        if(state.seeking!==transition)return;
        const q=clamp((now-begin)/duration);
        if(q>=.42&&!transition.captionSwitched){transition.captionSwitched=true;renderCaption();}
        if(p>0){state.p=p*ease(q);renderImplementation(target,state.p);updateTransport();}
        panel.style.opacity=String(q<.42?lerp(panelOpacity,0,ease(q/.42)):ease((q-.42)/.58));
        const fade=ease(q);
        field.style.opacity=String((p>0?Number(field.style.opacity||0):targetFieldOpacity)*fade);
        mesh.style.opacity=String((p>0?Number(mesh.style.opacity||0):targetMeshOpacity)*fade);
        const overlayTimelineOpacity=Number(overlay.getAttribute("opacity")||targetOverlayOpacity);
        const chartTimelineOpacity=Number(chart.getAttribute("opacity")||targetChartOpacity);
        overlay.style.opacity=String(overlayTimelineOpacity*fade);
        chart.style.opacity=String(chartTimelineOpacity*fade);
        leaving.style.opacity=String(1-fade);
        if(q<1)requestAnimationFrame(frame);
        else{
          state.seeking=null;clearImplementationFade();renderImplementation(target,state.p);updateTransport();
          if(state.playAfterSeek){state.playAfterSeek=false;play();}
        }
      });
      return;
    }
    const from=startStage+startP,to=target+p,begin=performance.now(),duration=clamp(Math.abs(to-from)*175+300,300,1000);
    state.seeking={begin,from,to,target,p,duration,lastDisplayed:startStage};
    requestAnimationFrame(function frame(now){
      if(!state.seeking||state.seeking.begin!==begin)return;
      const q=ease((now-begin)/duration),value=lerp(from,to,q);
      let step=Math.min(currentStages().length-1,Math.floor(value));let part=clamp(value-step);
      if(q>=1){step=target;part=p;state.seeking=null;}
      const changed=step!==state.stage;state.stage=step;state.p=part;
      if(changed||q>=1)renderCaption();render();
      if(q<1)requestAnimationFrame(frame);
      else if(state.playAfterSeek){state.playAfterSeek=false;play();}
    });
  }
  function play(){
    if(state.page===0)return;
    if(state.playing){stop();return;}
    if(state.seeking){state.playAfterSeek=!state.playAfterSeek;return;}
    state.seeking=null;
    if(state.p>=1){state.p=0;render();}
    else if(state.page===2&&state.p<=.001)renderImplementation(state.stage,0);
    state.playing=true;state.last=0;scene[state.page].classList.add("is-playing");syncAmbient();updateTransport();
    requestAnimationFrame(tick);
  }
  function tick(now){
    if(!state.playing)return;
    if(state.last){const dt=Math.min(now-state.last,80);state.p=clamp(state.p+dt/(currentStages()[state.stage].duration*1000));}
    state.last=now;
    render();
    if(state.p>=1){stop();return;}
    requestAnimationFrame(tick);
  }
  function setPage(page){
    const next=clamp(page,0,2);
    if(next===state.page)return;
    state.playing=false;state.seeking=null;state.playAfterSeek=false;state.basisTransition=null;state.last=0;state.ambientPaused=false;clearKnowledgeFade();clearImplementationFade();scene[1].classList.remove("is-playing","is-basis-changing");scene[2].classList.remove("is-playing");
    scene[state.page].classList.remove("is-active");scene[state.page].classList.add("is-exiting");scene[state.page].setAttribute("inert","");
    state.page=next;state.stage=0;state.requestedStage=0;state.p=0;
    scene[next].classList.remove("is-exiting");scene[next].classList.add("is-active");scene[next].removeAttribute("inert");
    syncAmbient();
    $("transport").hidden=next===0;
    document.querySelectorAll(".page-dots button").forEach(b=>{
      const active=Number(b.dataset.page)===next;
      b.classList.toggle("active",active);
      if(active)b.setAttribute("aria-current","page");else b.removeAttribute("aria-current");
    });
    if(next!==0){buildStageList();renderCaption();render();}
  }

  buildCover();buildGlobalMesh();buildImplementationMesh();buildImplementationField();renderKnowledge(0);
  $("enterKnowledge").addEventListener("click",()=>setPage(1));
  $("cover").addEventListener("click",e=>{if(e.target.closest("button"))return;setPage(1);});
  document.querySelectorAll(".page-dots button").forEach(b=>b.addEventListener("click",()=>setPage(Number(b.dataset.page))));
  $("previousPage").addEventListener("click",()=>setPage(state.page-1));
  $("nextPage").addEventListener("click",()=>setPage(state.page+1));
  $("previousStage").addEventListener("click",()=>seekStage(state.requestedStage-1,0));
  $("nextStage").addEventListener("click",()=>seekStage(state.requestedStage+1,0));
  $("stageStart").addEventListener("click",()=>seekStage(state.requestedStage,0));
  $("stageEnd").addEventListener("click",()=>seekStage(state.requestedStage,1));
  $("playPause").addEventListener("click",play);
  $("ambientToggle").addEventListener("click",()=>{
    state.ambientPaused=!state.ambientPaused;
    syncAmbient();updateTransport();
  });
  $("timeline").addEventListener("input",e=>{
    if(state.seeking){state.stage=state.requestedStage;renderCaption();}
    state.seeking=null;state.playAfterSeek=false;clearKnowledgeFade();clearImplementationFade();state.playing=false;scene[state.page].classList.remove("is-playing");state.p=Number(e.target.value)/1000;state.last=0;syncAmbient();render();
  });
  let modelSwapTimer=null;
  document.querySelectorAll("[data-model]").forEach(b=>b.addEventListener("click",()=>{
    if(state.model===b.dataset.model)return;
    const panel=document.querySelector(".implementation-content");
    panel.classList.add("is-changing");
    clearTimeout(modelSwapTimer);
    modelSwapTimer=setTimeout(()=>{
      state.model=b.dataset.model;renderCaption();render();
      panel.classList.remove("is-changing");
    },reduced.matches?0:180);
  }));
  document.addEventListener("keydown",e=>{
    if(["INPUT","TEXTAREA"].includes(document.activeElement?.tagName))return;
    if(e.code==="Space"&&state.page!==0){e.preventDefault();play();}
    else if(e.key==="ArrowRight"&&state.page!==0){e.preventDefault();seekStage(state.requestedStage+1,0);}
    else if(e.key==="ArrowLeft"&&state.page!==0){e.preventDefault();seekStage(state.requestedStage-1,0);}
    else if(e.key==="ArrowDown")setPage(state.page+1);
    else if(e.key==="ArrowUp")setPage(state.page-1);
  });
  let wheelReady=true;
  document.addEventListener("wheel",e=>{if(!wheelReady||Math.abs(e.deltaY)<18)return;if(state.page===0||state.page===2||state.page===1&&e.shiftKey){wheelReady=false;setPage(state.page+(e.deltaY>0?1:-1));setTimeout(()=>wheelReady=true,700);}}, {passive:true});
  let touchOrigin=null;
  document.addEventListener("touchstart",e=>{
    if(e.touches.length!==1||e.target.closest("button,input,.implementation-content")){touchOrigin=null;return;}
    touchOrigin={x:e.touches[0].clientX,y:e.touches[0].clientY};
  },{passive:true});
  document.addEventListener("touchend",e=>{
    if(!touchOrigin||!e.changedTouches.length)return;
    const dx=e.changedTouches[0].clientX-touchOrigin.x,dy=e.changedTouches[0].clientY-touchOrigin.y;
    touchOrigin=null;
    if(Math.abs(dy)>80&&Math.abs(dy)>Math.abs(dx)*1.3)setPage(state.page+(dy<0?1:-1));
  },{passive:true});
})();
