import numpy as np
from bresenham import bresenham
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi, voronoi_plot_2d


def create_grid_and_edges(data, drone_altitude):
    """
    Returns a grid representation of a 2D configuration space
    along with Voronoi graph edges given obstacle dat and the 
    drone's altitude.
    """
    # minimum and maximum north coordinates
    north_min = np.floor(np.amin(data[:, 0] - data[:, 3]))
    north_max = np.ceil(np.amax(data[:, 0] + data[:, 3]))

    # minimum and maximum east coordinates
    east_min = np.floor(np.amin(data[:, 1] - data[:, 4]))
    east_max = np.ceil(np.amax(data[:, 1] + data[:, 4]))

    # given the minimum and maximum coordinates we can
    # calcuulate the size of the grid
    north_size = int(np.ceil((north_max - north_min)))
    east_size = int(np.ceil((east_max - east_min)))
    
    # create an empty grid and points list
    grid = np.zeros((north_size, east_size))
    points = []

    for i in range(data.shape[0]):
        north, east, alt, d_north, d_east, d_alt = data[i, :]
        if alt + d_alt > drone_altitude:
            obstacle = [
                int(north - d_north - north_min),
                int(north + d_north - north_min),
                int(east - d_east - east_min),
                int(east + d_east - east_min)
            ]

            grid[obstacle[0]:obstacle[1], obstacle[2]:obstacle[3]] = 1
            # add center of obstacles to points list
            points.append([north - north_min, east - east_min])

    # ceate a voronoi graph based on location of obstacle centres
    graph = Voronoi(points)
    # check each edge from graph.ridge_vertices from collision
    edges = []
    for v in graph.ridge_vertices:
        p1 = graph.vertices[v[0]]
        p2 = graph.vertices[v[1]]
        cells = list(bresenham(int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1])))
        hit = False

        for c in cells:
            # check if off the map
            if np.amin(c) < 0 or c[0] >= grid.shape[0] or c[1] >= grid.shape[1]:
                hit = True
                break

            # check if in collision
            if grid[c[0], c[1]] == 1:
                hit = True
                break

        # if the edge does not hit on obstacle
        # add it to the list
        if not hit:
            p1 = (p1[0], p1[1])
            p2 = (p2[0], p2[1])
            edges.append((p1, p2))

    return grid, edges



def plot(grid, edges):
    plt.imshow(grid, origin='lower', cmap='Greys')
    for e in edges:
        p1 = e[0]
        p2 = e[1]
        plt.plot([p1[1], p2[1]], [p1[0], p2[0]], 'b-')

    plt.xlabel('EAST')
    plt.ylabel('NORTH')
    plt.show()


if __name__ == '__main__':
    filename = "colliders.csv"
    data = np.loadtxt(filename, delimiter=',', dtype="Float64", skiprows=2)
    
    drone_altitude = 5
    grid, edges = create_grid_and_edges(data, drone_altitude)
    print('Found %5d edges' % len(edges)) 

    plot(grid, edges)
