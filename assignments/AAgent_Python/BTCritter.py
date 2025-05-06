import asyncio
import random
import py_trees
import py_trees as pt
from py_trees import common
import Goals_BT
import Sensors

# BEHAVIOUR: Agent not doing random moves
class BN_Avoid(pt.behaviour.Behaviour):
    """Behaviour‐tree node wrapping our Goals_BT.Avoid obstacle‐avoider."""
    def __init__(self, aagent):
        super(BN_Avoid, self).__init__("BN_Avoid")
        self.my_agent = aagent
        self._task = None

    def initialise(self):
        # start the Avoid.run() coroutine
        self._task = asyncio.create_task(Goals_BT.Avoid(self.my_agent).run())

    def update(self):
        if not self._task.done():
            return pt.common.Status.RUNNING
        return pt.common.Status.SUCCESS  # Avoid never “fails”
    
    def terminate(self, new_status):
        if self._task:
            self._task.cancel()

# BEHAVIOUR: Agent will return SUCCESS iff it has a flower in sight
class BN_DetectFlower(pt.behaviour.Behaviour):
    def __init__(self, aagent):
        self.my_goal = None
        # print("Initializing BN_DetectFlower")
        super(BN_DetectFlower, self).__init__("BN_DetectFlower")
        self.my_agent = aagent

    def initialise(self):
        pass

    def update(self):
        sensor_obj_info = self.my_agent.rc_sensor.sensor_rays[Sensors.RayCastSensor.OBJECT_INFO]
        for index, value in enumerate(sensor_obj_info):
            if value:  # there is a hit with an object
                if value["tag"] == "AlienFlower":  # If it is a flower
                    # print("Flower detected!")
                    # print("BN_DetectFlower completed with SUCCESS")
                    return pt.common.Status.SUCCESS
        # print("No flower...")
        # print("BN_DetectFlower completed with FAILURE")
        return pt.common.Status.FAILURE

    def terminate(self, new_status: common.Status):
        pass

# BEHAVIOUR: The agent will rotate until it's facing a flower
class BN_FaceFlower(pt.behaviour.Behaviour):
    def __init__(self, aagent):
        self.my_goal = None
        # print("Initializing BN_FaceFlower")
        super(BN_FaceFlower, self).__init__("BN_FaceFlower")
        self.my_agent = aagent

    def initialise(self):
        self.my_goal = asyncio.create_task(Goals_BT.FaceFlower(self.my_agent).run())

    def update(self):
        if not self.my_goal.done():
            # print("BN_FaceFlower completed with RUNNING")
            return pt.common.Status.RUNNING
        else:
            res = self.my_goal.result()
            if res:
                print("BN_FaceFlower completed with SUCCESS")
                return pt.common.Status.SUCCESS
            else:
                print("BN_FaceFlower completed with FAILURE")
                return pt.common.Status.FAILURE

    def terminate(self, new_status: common.Status):
        self.my_goal.cancel()    

# BEHAVIOUR: Walk towards the flower (Agent has to already be facing the right direction)
class BN_WalkToFlower(pt.behaviour.Behaviour):
    def __init__(self, aagent):
        self.my_goal = None
        # print("Initializing BN_WalkToFlower")
        super(BN_WalkToFlower, self).__init__("BN_WalkToFlower")
        self.my_agent = aagent

    def initialise(self):
        self.my_goal = asyncio.create_task(Goals_BT.WalkToFlower(self.my_agent).run())

    def update(self):
        if not self.my_goal.done():
            return pt.common.Status.RUNNING
        else:
            res = self.my_goal.result()
            if res:
                print("BN_WalkToFlower completed with SUCCESS")
                return pt.common.Status.SUCCESS
            else:
                print("BN_WalkToFlower completed with FAILURE")
                return pt.common.Status.FAILURE

    def terminate(self, new_status: common.Status):
        self.my_goal.cancel()

# BEHAVIOUR: Detect astronaut
class BN_DetectAstronaut(pt.behaviour.Behaviour):
    def __init__(self, aagent):
        self.my_goal = None
        # print("Initializing BN_DetectAstronaut")
        super(BN_DetectAstronaut, self).__init__("BN_DetectAstronaut")
        self.my_agent = aagent

    def initialise(self):
        pass

    def update(self):
        sensor_obj_info = self.my_agent.rc_sensor.sensor_rays[Sensors.RayCastSensor.OBJECT_INFO]
        for index, value in enumerate(sensor_obj_info):
            if value:  # there is a hit with an object
                if value["tag"] == "Astronaut":  # If it is an Astronaut
                    # print("Astronaut detected!")
                    print("BN_DetectAstronaut completed with SUCCESS")
                    return pt.common.Status.SUCCESS
        # print("No Astronaut...")
        # print("BN_DetectAstronaut completed with FAILURE")
        return pt.common.Status.FAILURE

    def terminate(self, new_status: common.Status):
        pass

# BEHAVIOUR: The agent will rotate until it's facing a flower
class BN_FaceAstronaut(pt.behaviour.Behaviour):
    def __init__(self, aagent):
        self.my_goal = None
        # print("Initializing BN_FaceAstronaut")
        super(BN_FaceAstronaut, self).__init__("BN_FaceAstronaut")
        self.my_agent = aagent
        self.last_astronaut_idx = None

    def initialise(self):
        self.my_goal = asyncio.create_task(Goals_BT.FaceAstronaut(self.my_agent).run())

    def update(self):
        if not self.my_goal.done():
            # print("BN_FaceAstronaut completed with RUNNING")
            return pt.common.Status.RUNNING
        else:
            res = self.my_goal.result()
            if res:
                print("BN_FaceAstronaut completed with SUCCESS")
                return pt.common.Status.SUCCESS
            else:
                print("BN_FaceAstronaut completed with FAILURE")
                return pt.common.Status.FAILURE

    def terminate(self, new_status: common.Status):
        self.my_goal.cancel()  

# BEHAVIOUR: Walk towards the astronaut (Agent has to already be facing the right direction)
class BN_ChaseAstronaut(pt.behaviour.Behaviour):
    def __init__(self, aagent):
        self.my_goal = None
        # print("Initializing BN_ChaseAstronaut")
        super(BN_ChaseAstronaut, self).__init__("BN_ChaseAstronaut")
        self.my_agent = aagent

    def initialise(self):
        self.my_goal = asyncio.create_task(Goals_BT.WalkToAstronaut(self.my_agent).run())

    def update(self):
        if not self.my_goal.done():
            return pt.common.Status.RUNNING
        else:
            res = self.my_goal.result()
            if res:
                print("BN_ChaseAstronaut completed with SUCCESS")
                return pt.common.Status.SUCCESS
            else:
                print("BN_ChaseAstronaut completed with FAILURE")
                return pt.common.Status.FAILURE

    def terminate(self, new_status: common.Status):
        self.my_goal.cancel()

class BN_Retreat(pt.behaviour.Behaviour):
    def __init__(self, aagent):
        self.my_goal = None
        # print("Initializing BN_Retreat")
        super(BN_Retreat, self).__init__("BN_Retreat")
        self.my_agent = aagent

    def initialise(self):
        self.my_goal = asyncio.create_task(Goals_BT.Retreat(self.my_agent).run())

    def update(self):
        if not self.my_goal.done():
            return pt.common.Status.RUNNING
        else:
            res = self.my_goal.result()
            if res:
                print("BN_Retreat completed with SUCCESS")
                return pt.common.Status.SUCCESS
            else:
                print("BN_Retreat completed with FAILURE") # Cannot Fail
                return pt.common.Status.FAILURE

    def terminate(self, new_status: common.Status):
        self.my_goal.cancel()



class BTCritter:
    def __init__(self, aagent):
        # py_trees.logging.level = py_trees.logging.Level.DEBUG

        self.aagent = aagent

        # FINAL VERSION
        # Chase astronaut logic
        chase = pt.composites.Sequence(name="DetectFlower", memory=True)
        chase.add_children([BN_DetectAstronaut(aagent), BN_FaceAstronaut(aagent), BN_ChaseAstronaut(aagent), BN_Retreat(aagent)])

        # Gather flower logic
        detection = pt.composites.Sequence(name="DetectFlower", memory=True)
        detection.add_children([BN_DetectFlower(aagent), BN_FaceFlower(aagent), BN_WalkToFlower(aagent)])

        # Roaming logic
        # roaming = pt.composites.Parallel("Parallel", policy=py_trees.common.ParallelPolicy.SuccessOnAll())
        # roaming.add_children([BN_ForwardRandom(aagent), BN_TurnRandom(aagent)])
        roaming = pt.composites.Sequence(name="Roaming", memory=False)
        roaming.add_child(BN_Avoid(aagent))
        
        self.root = pt.composites.Selector(name="Selector", memory=False)
        self.root.add_children([chase, roaming]) # Detection not on the tree for the time being

        self.behaviour_tree = pt.trees.BehaviourTree(self.root)

    # Function to set invalid state for a node and its children recursively
    def set_invalid_state(self, node):
        node.status = pt.common.Status.INVALID
        for child in node.children:
            self.set_invalid_state(child)

    def stop_behaviour_tree(self):
        # Setting all the nodes to invalid, we force the associated asyncio tasks to be cancelled
        self.set_invalid_state(self.root)

    async def tick(self):
        self.behaviour_tree.tick()
        await asyncio.sleep(0)
