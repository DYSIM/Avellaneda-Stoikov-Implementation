from scipy.stats import norm
import numpy as np
import matplotlib.pyplot as plt

def brownian_motion(s_0, n, sigma, dt):
    """Simulate prices with brownian motion and an upward drift
    """
    r = norm.rvs(size=(n,), scale=sigma*np.sqrt(dt))

    res = np.empty(r.shape)

    np.cumsum(r, axis=-1, out=res)
    res += np.array([s_0])

    #slight upward drift
    res = [x + 0.01 * ind for ind,x in enumerate(res)]
    return res


if __name__ == "__main__":
    res = brownian_motion(100, 200, 2, 0.005)
    # print(type(res))
    # print(len(res))
    plt.plot(res)
    plt.savefig('brownian.png')
