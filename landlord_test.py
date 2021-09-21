from typing import Optional, List
from pydantic import constr
import sqlite3
import matplotlib.pyplot as plt

ALPHA = 0.3

container_specs = []

class ContainerSpec:
    """Software specification for a container.

    Accepts the following software requirements:
    - `apt`: list of package names to be installed via apt-get
    - `pip`: list of pip requirements (name and optional version specifier)
    - `conda`: list of conda requirements (name and optional version specifier)

    To specify the version of Python to use, include it in the
    `conda` package list.
    """

    # regex borrowed from repo2docker (sort of...)
    # https://github.com/jupyterhub/repo2docker/blob/560b1d96a0e39cb8de53cb41a7c2d8d23384eb82/repo2docker/buildpacks/base.py#L675
    apt: Optional[List[constr(regex=r'^[a-z0-9.+-]+$')]]  # noqa: F722
    pip: Optional[List[str]]
    conda: Optional[List[str]]

    def __init__(self, apt, pip, conda):
        self.apt = apt
        self.pip = pip
        self.conda = conda

    def merge_spec(self, target):
        if target.apt != []:
            self.apt.extend(target.apt)
            self.apt = list(set(self.apt))
        if target.pip != []:
            self.pip.extend(target.pip)
            self.pip = list(set(self.pip))
        if target.conda != []:
            self.conda.extend(target.conda)
            self.conda = list(set(self.conda))


# The smaller Jaccard distence is, the more alike the two sets are.
def jaccard(a, b):
    return 1 - float(len(a & b))/len(a | b)


def spec_to_set(spec):
    out = set()
    if spec.apt:
        out.update({f'a{x}' for x in spec.apt})
    if spec.conda:
        out.update({f'c{x}' for x in spec.conda})
    if spec.pip:
        out.update({f'p{x}' for x in spec.pip})
    return out


def check_compatibility(source, target):
    left = source - target
    right = target - source
    for l in left:
        indexl = l.find("==")
        if indexl == -1:
            continue
        for r in right:
            indexr = r.find("==")
            if indexr == -1:
                continue
            if l[0: indexl] == r[0: indexr] and l[indexl+2:] != r[indexr+2:]:
                return False
    return True


# Simply resuse larger container.
# When no larger container to use for some specs,
# check Jacaard distence to finde if there is some container to be merged
def find_existing(list, spec):
    if spec is None:
        return
    build = True
    merge = False
    target = spec_to_set(spec)
    best_distance = 2.0
    best_index = -1
    for index, container_spec in enumerate(list):
        other = spec_to_set(container_spec)
        distance = jaccard(target, other)
        if not target.issubset(other):
            # check Jaccard and do merge if possible
            if distance > ALPHA:
                continue
            elif check_compatibility(other, target) is True:
                if distance < best_distance:
                    best_distance = distance
                    best_index = index
        else:
            build = False
            break
    if build is True and best_index != -1:
        # do merge
        list[best_index].merge_spec(spec)
        merge = True
        build = False
    return merge, build

def row_element_2_list(row_element):
    element_string = str(row_element).replace('[', '').replace(']', '').replace('"', '').replace('"', '').replace(' ', '').replace('None', '')
    if element_string == '':
        return []
    else:
        return element_string.split(',')

if __name__ == '__main__':
    # print("main")
    conn = sqlite3.connect('binder.sqlite')
    cursor = conn.cursor()
    cursor.execute('select `pip_packages`, `apt_packages`, `conda_packages` from clean_specs where `pip_packages` != "None" OR `apt_packages` != "None" OR `conda_packages` != "None" LIMIT 50000')
    total_requests = 0
    build_cnt = 0
    merge_cnt = 0
    build_data = [0]
    merge_data = [0]
    for row in cursor:
        total_requests += 1
        build_spec = ContainerSpec(row_element_2_list(row[1]), row_element_2_list(row[0]), row_element_2_list(row[2]))
        merge, build = find_existing(container_specs, build_spec)
        if build is True:
            container_specs.append(build_spec)
            build_cnt += 1
        elif merge is True:
            merge_cnt += 1
        if total_requests % 100 is 0 and total_requests > 0:
            build_data.append(build_cnt)
            merge_data.append(merge_cnt)
            print("build " + str(build_cnt) + " times and merge " + str(merge_cnt) + " times in " + str(total_requests) + " requests")

    x = range(len(build_data))
    x_requests = [i*100 for i in range(0, len(build_data))]
    plt.style.use('ggplot')
    plt.figure()
    plt.title("Build count using LANDLORD and Binder dataset")
    plt.xlabel("requests")
    plt.ylabel("builds")
    plt.plot(x_requests, build_data, label = "BuildCount")
    plt.plot(x_requests, merge_data, label = "MergeCount")
    plt.legend()
    plt.grid(True)
    plt.show()
        
    
        