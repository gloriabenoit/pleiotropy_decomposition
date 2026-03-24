import sys

import matplotlib.pyplot as plt
import numpy as np
import polars as pl
import seaborn as sns

import scipy.spatial as sp, scipy.cluster.hierarchy as hc

def get_colors(columns):
    """Get column colors."""
    software_colors = {
        "SUPERGNOVA": "seagreen",
        "HDL-L": "cornflowerblue",
        "FactorGo": "firebrick",
        "GFA": "darkblue",
        "GLEANR": "darkorange",
        "GUIDE": "mediumorchid"
    }

    return [software_colors.get(col.split('.')[-1], "grey") for col in columns]

def format_corr_mat(filename):
    """Format correlation matrix"""
    corr_mat = pl.read_csv(filename).drop("")
    corr_mat = corr_mat.select(pl.all().cast(pl.Float64))
    ticklabels = corr_mat.columns
    tickcolors = get_colors(corr_mat.columns)

    corr_mat = corr_mat.to_numpy()
    return corr_mat, ticklabels, tickcolors

def make_heatmap(corr_mat, output, ticklabels="", tickcolors=""):
    """Compute correlation heatmap."""
    # plt.figure(figsize=(20, 20))
    # ax = sns.heatmap(corr_mat,
    #                  xticklabels=ticklabels, yticklabels=ticklabels,
    #                 #  annot=True, fmt=".2f", annot_kws={"fontsize":7},
    #                  cmap="coolwarm", cbar=False,
    #                  center=0, vmin=-1, vmax=1)
    # ax.xaxis.tick_top()
    # ax.set_xticklabels(ax.get_xticklabels(), rotation=90, ha="left")

    sns.clustermap(corr_mat,
                   xticklabels=ticklabels, yticklabels=ticklabels,
                   cmap="coolwarm", row_colors=tickcolors, col_colors=tickcolors,
                   center=0, vmin=-1, vmax=1, cbar_pos=None,
                   row_cluster=False, col_cluster=False, dendrogram_ratio=0.01,
                   figsize=(22, 22))

    plt.savefig(output, bbox_inches='tight')
    plt.close()

def make_cluster_heatmap(corr_mat, output, ticklabels="", tickcolors=""):
    """Compute clustered correlation heatmap."""
    # print(corr_mat.shape)
    # dissimilarity = 1 - abs(corr_mat)
    # dissimilarity = np.nan_to_num(dissimilarity)
    # print(dissimilarity)
    # ld_linkage = hc.linkage(sp.distance.squareform(dissimilarity), method='complete')
    # https://github.com/mwaskom/seaborn/issues/989
    # print(ld_linkage)

    # plt.figure(figsize=(20, 20))
    # ax = sns.clustermap(corr_mat,
    #                     row_linkage=ld_linkage, col_linkage=ld_linkage,
    #                     xticklabels=ticklabels, yticklabels=ticklabels,
    #                     cmap="coolwarm",
    #                     center=0, vmin=-1, vmax=1,
    #                     figsize=(20,20))

    # Source - https://stackoverflow.com/a/76042335
    # Posted by Martijn Courteaux
    # Retrieved 2026-03-19, License - CC BY-SA 4.0

    pdist_uncondensed = 1.0 - np.nan_to_num(corr_mat)
    pdist_condensed = np.concatenate([row[i+1:] for i, row in enumerate(pdist_uncondensed)])
    linkage = hc.linkage(pdist_condensed, method='complete')

    sns.clustermap(corr_mat,
                   xticklabels=ticklabels, yticklabels=ticklabels,
                   cmap="coolwarm", row_colors=tickcolors, col_colors=tickcolors,
                   center=0, vmin=-1, vmax=1, cbar_pos=None,
                   row_linkage=linkage, col_linkage=linkage, dendrogram_ratio=0.05,
                   figsize=(22, 22))
    # idx = hc.fcluster(linkage, 0.5 * pdist_condensed.max(), 'distance')
    # ax.cax.set_visible(False)

    plt.savefig(output, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    _, FILENAME, CORR_OUT, CLUSTER_CORR_OUT = sys.argv

    corr_mat, columns, colors = format_corr_mat(FILENAME)
    make_heatmap(corr_mat, CORR_OUT, ticklabels=columns, tickcolors=colors)
    make_cluster_heatmap(corr_mat, CLUSTER_CORR_OUT, ticklabels=columns, tickcolors=colors)
