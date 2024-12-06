import open3d as o3d
import numpy as np
import plotly.graph_objects as go
import os
from matplotlib import cm
from PIL import Image
import cv2


def extract_xyz(pcd_file):
    """Extract x, y, z coordinates from .pcd file"""
    pcd = o3d.io.read_point_cloud(pcd_file, format="pcd")
    points = np.asarray(pcd.points)
    x = points[:, 0]
    y = points[:, 1]
    z = points[:, 2]
    return x, y, z


def visualize_pcd(pcd_file):
    """Visualize point cloud"""
    pcd_x, pcd_y, pcd_z = extract_xyz(pcd_file)
    fig = go.Figure(
        data=[
            go.Scatter3d(
                x=pcd_x, y=pcd_y, z=pcd_z, mode="markers", marker=dict(size=2, opacity=0.8)
            ),
        ]
    )
    fig.update_layout(
        margin=dict(l=0, r=0, b=0, t=0),
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z",
            aspectmode="data",
        ),
    )
    fig.update_scenes(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False)
    fig.show()


def draw_projections_on_image(velo_uvz, image, save_path, preprocess=True, indexes=None):
    """Draw LiDAR point projectiins on the image"""
    if preprocess:
        # remove negative points
        velo_uvz = np.delete(velo_uvz, np.where(velo_uvz[2, :] < 0)[0], axis=1)

        # remove outliers
        u, v, z = velo_uvz
        img_h, img_w, _ = image.shape
        u_out = np.logical_or(u < 0, u > img_w)
        v_out = np.logical_or(v < 0, v > img_h)
        outliers = np.logical_or(u_out, v_out)
        velo_uvz = np.delete(velo_uvz, np.where(outliers), axis=1)

    # create color map
    u, v, z = velo_uvz
    rainbow_r = cm.get_cmap("rainbow_r", lut=100)
    color_map = lambda z: [255 * val for val in rainbow_r(int(z.round()))[:3]]

    # draw LiDAR point cloud on blank image
    for i in range(len(u)):
        if indexes and i in indexes:
            cv2.circle(image, (int(u[i]), int(v[i])), 1, color_map(z[i]), -1)

    if indexes:
        for i in indexes:
            cv2.circle(image, (int(u[i]), int(v[i])), 1, color_map(z[i]), -1)
    else:
        for i in range(len(u)):
            cv2.circle(image, (int(u[i]), int(v[i])), 1, color_map(z[i]), -1)

    # save result
    image = Image.fromarray(image)
    image.save(save_path)


def visualize_3d_masks(pcd_file, mask_indexes):
    """Draw 3D point cloud segmentation masks"""
    pcd = o3d.io.read_point_cloud(pcd_file, format="pcd")
    masked_pcd = pcd.select_by_index(mask_indexes)
    unmasked_pcd = pcd.select_by_index(mask_indexes, invert=True)

    masked_points = np.asarray(masked_pcd.points)
    unmasked_points = np.asarray(unmasked_pcd.points)

    masked_x = masked_points[:, 0]
    masked_y = masked_points[:, 1]
    masked_z = masked_points[:, 2]

    unmasked_x = unmasked_points[:, 0]
    unmasked_y = unmasked_points[:, 1]
    unmasked_z = unmasked_points[:, 2]

    fig = go.Figure(
        data=[
            go.Scatter3d(
                x=masked_x,
                y=masked_y,
                z=masked_z,
                mode="markers",
                marker=dict(size=2, opacity=1.0, color="red"),
                name="masked points",
                showlegend=True,
            ),
            go.Scatter3d(
                x=unmasked_x,
                y=unmasked_y,
                z=unmasked_z,
                mode="markers",
                marker=dict(size=2, opacity=0.8, color="royalblue"),
                name="other points",
                showlegend=True,
            ),
        ]
    )
    fig.update_layout(
        margin=dict(l=0, r=0, b=0, t=0),
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z",
            aspectmode="data",
        ),
    )
    fig.update_scenes(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False)
    fig.show()


