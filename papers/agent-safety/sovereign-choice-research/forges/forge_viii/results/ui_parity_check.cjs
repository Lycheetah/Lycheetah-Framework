'use strict';
// Run: node results/ui_parity_check.cjs
const fs=require('fs'),path=require('path'),assert=require('assert');
const root=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(root,'prototype/sovereignty_surface_lab.html'),'utf8');
const start=html.indexOf('const DATA = ')+ 'const DATA = '.length;
const end=html.indexOf(';\nconst scenario=',start);
assert(start>0 && end>start,'could not parse fixture data');
const DATA=JSON.parse(html.slice(start,end));
const fnStart=html.indexOf('function bestPath(');
const fnEnd=html.indexOf('const labels=',fnStart);
assert(fnStart>=0&&fnEnd>fnStart,'no comparator function');
const bestPath=new Function(html.slice(fnStart,fnEnd)+'return bestPath')();
const expected=JSON.parse(fs.readFileSync(path.join(root,'results/benchmark.json'),'utf8'));
let checked=0;
for(const row of expected.rows){
 const s=DATA[row.scenario];assert(s);
 for(const [side,verdict] of [['open',row.open_verdict],['constrained',row.constrained_verdict]]){
   const actual=bestPath(s,s[side],s.desired,s.budget);
   assert.strictEqual(actual.status,verdict,`${row.scenario} ${side}`);checked++;
 }
}
console.log(JSON.stringify({verified_fixture_comparisons:checked,passed:true,meaning:'JS and Python match for 16 fixture outcomes; does not establish real-world correctness'}));
