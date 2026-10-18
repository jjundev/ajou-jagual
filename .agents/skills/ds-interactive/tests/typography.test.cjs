const {test}=require('node:test'),a=require('node:assert/strict'),fs=require('node:fs'),p=require('node:path');
test('standalone typography uses real Pretendard 400/500/600/700 faces instead of stretching Regular',()=>{
 const file=p.join(__dirname,'../examples/0928/value-address.cjs');
 const {html}=require('../scripts/build.cjs').buildPage({scenario:{definition:require(file),sourceText:fs.readFileSync(file,'utf8')}});
 for(const [name,weight] of [['Regular',400],['Medium',500],['SemiBold',600],['Bold',700]]){
  const face=[...html.matchAll(/@font-face\{([^}]+)\}/g)].find(m=>m[1].includes(`font-weight:${weight};`));
  a.ok(face,`missing real weight ${weight}`);a.match(face[1],/font-family:Pretendard;/);
  a.ok(face[1].includes(fs.readFileSync(p.join(__dirname,`../assets/vendor/pretendard/Pretendard-${name}.woff2`)).toString('base64')));
 }
 a.ok(!html.includes('font-weight:100 900'),'static Regular cannot advertise variable weights');
});
