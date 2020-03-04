"""
Data utilities
"""
###########
# Imports #
###########
import praw
import networkx as nx
import re

#############
# Utilities #
#############


def extract_data(redditor, limit=None):
    """
    Extract the data using Reddit API via PRAW

    Input:
    limit: maximum number of comments to retrieve. (default: None - means as much as possible)

    Outputs:
    labels: dictionary with subreddits names as keys and their associated number in the graph as values
    edges: dictionary with subreddits number as keys and their associated dictionary as values
        Each key entry has a nested dictionary which contains the subreddits it is linked to as keys
            and the number of links as values (which will serve later as weight)
    """


    labels = dict()
    edges = dict()
    index = 0

    for comment in redditor.comments.top(limit=limit):
        sub = comment.subreddit_name_prefixed

        if sub not in labels.keys():
            labels[sub] = index
            index += 1

        match = re.search(r'\[\/r\/\w+\]', comment.body).group(0)
        link = match[2 : len(match) - 1]

        if link not in labels.keys():
            labels[link] = index
            index += 1

        min_index, max_index = sorted((labels[sub], labels[link]))


        if min_index not in edges.keys():
            edges[min_index] = dict({max_index: 1})

        else:
            if max_index not in edges[min_index].keys():
                edges[min_index][max_index] = 1
            else:
                edges[min_index][max_index] += 1
    print(f"Number of nodes in the dataset: {len(labels)}")
    return labels, edges


def dic_to_str(dic, nested=False):
    """
    Transform a dictionary to an adequate string to be later saved in the 'label.txt' and 'edge.txt' files.
    Inputs:
    dic: dictionary to be transformed
    nested: boolean equals to True in case edges dictionary is to be transformed (False by default)
    Output:
    string: resulting string
    """
    string = ""
    if nested:
        for key in dic.keys():
            for nested_key in dic[key].keys():
                string += str(key) + " " + str(nested_key) + " " + str(dic[key][nested_key]) + "\n"
    else:
        for key in dic.keys():
            string += key + "\n"
    return string

def save_data(labels, edges, dataset_path):
    """
    Save the data into 3 separate files : 'type.txt', 'label.txt' and 'edge.txt' to be used to import the graph
    Inputs:
    labels: dictionary with subreddits names as keys and their associated number in the graph as values
    edges: dictionary with subreddits number as keys and their associated dictionary as values
        Each key entry has a nested dictionary which contains the subreddits it is linked to as keys
            and the number of links as values (which will serve later as weight)
    directory: directory name (default: directory defined at the top)
    dataset: dataset name (default: subreddits)
    Output:
    True if no error encoutered
    """
    with open(dataset_path +  '/type.txt', 'w') as file:
        graph_type ="UW" # Undirected, Weighted graph
        file.write(graph_type)
    with open(dataset_path + '/label.txt', 'w') as file:
        data = dic_to_str(labels)
        file.write(data)
    with open(dataset_path +'/edge.txt', 'w') as file:
        data = dic_to_str(edges, nested=True)
        file.write(data)
    return True

def import_graph(dataset_path):
    try:
        with open(dataset_path + "/type.txt", "r") as file:
            graph_type = file.readline()
        if graph_type == "DW":
            G = nx.read_weighted_edgelist(dataset_path + "/edge.txt",
                                          nodetype=int,
                                          create_using=nx.DiGraph())
        elif graph_type == "UW":
            G = nx.read_weighted_edgelist(dataset_path + "/edge.txt", nodetype=int)
        elif graph_type == "DU":
            G = nx.read_edgelist(dataset_path + "/edge.txt",
                                 nodetype=int,
                                 create_using=nx.DiGraph())
        else:
            G = nx.read_edgelist(dataset_path + "/edge.txt",
                                 nodetype=int)
        G.name = "subreddits"
    except:
        G = nx.Graph(name = "Empty graph")
    # Some info
    print (nx.info(G))
    return G
