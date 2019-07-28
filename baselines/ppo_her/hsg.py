from copy import copy, deepcopy
import random

class HSG(object):
    """ generate hindsight trajectories for input trajectories, based on the strategy update the desired goal of
    observations in the trajectory and recompute the rewards  """

    def __init__(self, reward_fn, *args, **kwargs):
        self.compute_reward = reward_fn
        self.multiplier = 0

    def get(self, trajectories):

        # Note: The reward for the last transiton of the trajectory cannot be computed as the obs after
        # last action is not available. We can ignore this last step and consider the step before it
        # as the last - resulting in a trajectory shorter by a step.

        trajectories = deepcopy(trajectories)
        hs_trajectories = []
        for trajectory in trajectories:
            hs_trajectories.extend(self._get(trajectory))

        return hs_trajectories

    def _get(self, trajectory):
        return []


class HSGFinal(HSG):

    def __init__(self, reward_fn, *args, **kwargs):
        HSG.__init__(self, reward_fn, *args, **kwargs)
        self.multiplier = 1

    def _get(self, trajectory):
        trajectory.pop()  # remove last step as the last obs is not useful in computing reward
        # change the desired goal to last obs' achieved_goal
        trajectory.update_obs('desired_goal', trajectory.obs[-1]['achieved_goal'].copy())
        trajectory.update_rewards(self.compute_reward)
        return [trajectory]


class HSGFuture(HSG):
    def __init__(self, reward_fn, *args, **kwargs):
        HSG.__init__(self, reward_fn, *args, **kwargs)

    def _get(self, trajectory):
        raise NotImplementedError


class HSGRandom(HSG):
    def __init__(self, reward_fn, *args, **kwargs):
        HSG.__init__(self, reward_fn, *args, **kwargs)

    def _get(self, trajectory):
        raise NotImplementedError


class HSGSplit(HSG):
    def __init__(self, reward_fn, splits=2, *args, **kwargs):
        HSG.__init__(self, reward_fn, *args, **kwargs)
        self.multiplier = 1
        self.k = splits

    def _get(self, trajectory):
        """ split the trajectory into k pieces """
        k = self.k
        if len(trajectory) < k:
            return [trajectory]
        trajs = trajectory.split(k)
        for traj in trajs:
            traj.update_obs('desired_goal', traj.obs[-1]['achieved_goal'].copy())
            traj.update_rewards(self.compute_reward)
        return trajs

class HSGRandomSub(HSG):
    def __init__(self, reward_fn, nsub=2, *args, **kwargs):
        HSG.__init__(self, reward_fn, *args, **kwargs)
        self.multiplier = 1
        self.k = nsub

    def _get(self, trajectory):
        trajs = []
        for k in range(self.k):
            i1, i2 = random.sample(range(len(trajectory)), 2)
            if i2 < i1:
                i1_temp = i1
                i1 = i2
                i2 = i1_temp
            trajs.append(trajectory.sub(i1, i2))
        return trajs

def get_hsg(strategy='none', reward_fn=None):
    assert callable(reward_fn)
    if strategy == 'none':
        return HSG(reward_fn)
    elif strategy == 'final':
        return HSGFinal(reward_fn)
    elif strategy == 'future':
        return HSGFuture(reward_fn)
    elif strategy == 'random':
        return HSGRandom(reward_fn)
    elif 'split' in strategy:
        return HSGSplit(reward_fn, int(copy(strategy).replace('split', '')))
    elif 'randomsub' in strategy:
        return HSGRandomSub(reward_fn, int(copy(strategy).replace('randomsub', '')))
    else:
        raise ValueError('unknwon reward function')

