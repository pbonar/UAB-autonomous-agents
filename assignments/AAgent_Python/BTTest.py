import py_trees as pt
import asyncio
import BTAstronautAlone

class BTAO:
    def __init__(self, aagent):
        self.aagent = aagent

        # Root node is a Sequence with a single child
        self.root = pt.composites.Sequence(name="GoToFlowerOnly", memory=True)
        self.root.add_child(BTAstronautAlone.BN_GoToFlower(aagent))

        self.behaviour_tree = pt.trees.BehaviourTree(self.root)

    # Optional utility to stop/cancel behavior
    def set_invalid_state(self, node):
        node.status = pt.common.Status.INVALID
        for child in node.children:
            self.set_invalid_state(child)

    def stop_behaviour_tree(self):
        self.set_invalid_state(self.root)

    async def tick(self):
        self.behaviour_tree.tick()
        await asyncio.sleep(0)
