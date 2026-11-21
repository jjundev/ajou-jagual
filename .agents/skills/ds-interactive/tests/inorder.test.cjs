const {test} = require('node:test');
const assert = require('node:assert/strict');
const {checkScenario} = require('../assets/engine/trace.js');
const {getTreeView} = globalThis.DSInteractive;
const examples = require('node:fs');
const fixturePath = require('node:path').join(__dirname,'../examples/1105/inorder.cjs');

test('inorder runs all three cases and returns to the right line', () => {
 assert.ok(examples.existsSync(fixturePath),'1105 inorder scenario must be available');
 const result=checkScenario(require(fixturePath));
 assert.equal(result.ok,true,JSON.stringify(result.issues));
 const {default:intro,lecture,empty}=result.traces;
 assert.equal(intro.snapshots.at(-1).state.stdout.join(''),'1 3 8 10 ');
 assert.equal(lecture.snapshots.at(-1).state.stdout.join(''),'3 7 12 18 26 27 31 ');
 assert.deepEqual(empty.snapshots.at(-1).state.stdout,[]);
 assert.equal(empty.lineSteps.length,3);
 assert.equal(empty.lineSteps.at(-1).next,null);

 const leftIndex=intro.lineSteps.findIndex(step=>{
  const edge=getTreeView(intro.metadata.tree,step).nullEdge;
  return edge?.nodeId==='node-1'&&edge.side==='left';
 });
 const [leftNull,afterLeftNull,afterFirstPrint,rightNull,afterRightNull]=intro.lineSteps.slice(leftIndex,leftIndex+5);
 const leafFrame=afterLeftNull.next.frameId;
 assert.equal(leftNull.next.at.line,2);
 assert.equal(leftNull.state.frames[leftNull.next.frameId].argumentSourceCellId,'node-1.left');
 assert.equal(leftNull.state.cells[leftNull.next.frameId+'.p'].value.target,null);
 assert.equal(afterLeftNull.next.at.line,4);
 assert.equal(afterLeftNull.state.frames[leftNull.next.frameId].lifetime,'ended');
 assert.deepEqual(afterLeftNull.state.stdout,[]);
 assert.equal(afterFirstPrint.state.stdout.join(''),'1 ');
 assert.equal(getTreeView(intro.metadata.tree,rightNull).nullEdge.side,'right');
 assert.equal(afterRightNull.next.at.line,6);
 assert.equal(afterRightNull.next.frameId,leafFrame);
 assert.equal(getTreeView(intro.metadata.tree,afterFirstPrint).nodes.find(n=>n.id==='node-1').outputOrder,1);
});
