import asyncio
import random
import py_trees
import py_trees as pt
from py_trees import common
import Goals_BT
import Sensors

# ===========================
# BEHAVIOUR: Agent will avoid obstacles
# ===========================
class BN_Avoid(pt.behaviour.Behaviour):
    """
    Behaviour‐tree node wrapping our Goals_BT.Avoid obstacle‐avoider.
    """
    def __init__(self, aagent):
        super(BN_Avoid, self).__init__("BN_Avoid")
        self.my_agent = aagent
        self._task = None

    def initialise(self):
        self._task = asyncio.create_task(Goals_BT.Avoid(self.my_agent).run())

    def update(self):
        if not self._task.done():
            return pt.common.Status.RUNNING
        return pt.common.Status.SUCCESS  # Avoid never “fails”
    
    def terminate(self, new_status):
        if self._task:
            self._task.cancel()

# ===========================
# BEHAVIOUR: Detecting Flowers
# ===========================
class BN_DetectFlower(pt.behaviour.Behaviour):
    """
    Agent will return SUCCESS iff it has a flower in sight
    """
    def __init__(self, aagent):
        self.my_goal = None
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

# ===========================
# BEHAVIOUR: Facing the flower
# ===========================
class BN_FaceFlower(pt.behaviour.Behaviour):
    """
    The agent will rotate until it's facing a flower
    """
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

# ===========================
# BEHAVIOUR: Walking to the flower
# ===========================
class BN_WalkToFlower(pt.behaviour.Behaviour):
    """
    Agent walks towards the flower (Agent has to already be facing the right direction)
    """
    def __init__(self, aagent):
        self.my_goal = None
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

# ===========================
# BEHAVIOUR: Detecting astronaut
# ===========================
class BN_DetectAstronaut(pt.behaviour.Behaviour):
    """
    Agent will return SUCCESS iff it has an astronaut in sight
    """
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

        return pt.common.Status.FAILURE

    def terminate(self, new_status: common.Status):
        pass

# ===========================
# BEHAVIOUR: Facing the astronaut
# ===========================
class BN_FaceAstronaut(pt.behaviour.Behaviour):
    """
    The agent will rotate until it's facing a flower
    """
    def __init__(self, aagent):
        self.my_goal = None
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

# ===========================
# BEHAVIOUR: Chasing the astronaut
# ===========================
class BN_ChaseAstronaut(pt.behaviour.Behaviour):
    """
    Walk towards the astronaut (Agent has to already be facing the right direction)
    """
    def __init__(self, aagent):
        self.my_goal = None
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

# ===========================
# BEHAVIOUR: Retreat from the astronaut
# ===========================
class BN_Retreat(pt.behaviour.Behaviour):
    """
    Agent will retreat from the astronaut so that it is able to go back to picking flowers
    """
    def __init__(self, aagent):
        self.my_goal = None
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


# ===========================
# BEHAVIOUR TREE: BTCritter
# ===========================
class BTCritter:
    """
    The agent will chase the astronaut and avoid obstacles
    """
    def __init__(self, aagent):
        """
        Initializes the behaviour tree for the critter agent.
        """
        self.aagent = aagent

        # Chase astronaut logic
        chase = pt.composites.Sequence(name="DetectFlower", memory=True)
        chase.add_children([BN_DetectAstronaut(aagent), BN_FaceAstronaut(aagent), BN_ChaseAstronaut(aagent), BN_Retreat(aagent)])


        # Roaming logic
        roaming = pt.composites.Sequence(name="Roaming", memory=False)
        roaming.add_child(BN_Avoid(aagent))
        
        # Selector node
        self.root = pt.composites.Selector(name="Selector", memory=False)
        self.root.add_children([chase, roaming])

        self.behaviour_tree = pt.trees.BehaviourTree(self.root)

    def set_invalid_state(self, node):
        """
        Sets the status of a node and its children to INVALID.
        """
        node.status = pt.common.Status.INVALID
        for child in node.children:
            self.set_invalid_state(child)

    def stop_behaviour_tree(self):
        """
        Stops the behaviour tree by setting all nodes to INVALID.
        """
        self.set_invalid_state(self.root)

    async def tick(self):
        """
        Ticks the behaviour tree.
        """    
        self.behaviour_tree.tick()
        await asyncio.sleep(0)
