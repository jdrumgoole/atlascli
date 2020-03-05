from mongodbatlas.atlaskey import AtlasKey
from mongodbatlas.atlasapi import AtlasAPI
from mongodbatlas.atlasorganization import AtlasOrganization
from mongodbatlas.atlascluster import AtlasCluster
from mongodbatlas.atlasproject import AtlasProject


class OPCAPI:
    """
    OPC API : Organizations, Projects Clusters.
    This API uses the Python objects for Organizations and clusters as opposed
    to the AtlasAPI which returns dicts.
    """

    def __init__(self, atlas_key:AtlasKey=None):
        self._atlas_api =AtlasAPI(atlas_key)

    """
    Organizations
    """
    def get_this_organization(self):
        org = self._atlas_api.get_this_organization()
        return AtlasOrganization(org)

    def get_organization_and_projects(self):
        org = self._atlas_api.get_this_organization()
        atlas_org = AtlasOrganization(org)
        projects = self.get_projects()
        atlas_org.add_projects(projects)
        return atlas_org

    def get_organization_and_clusters(self):
        org = self._atlas_api.get_this_organization()
        atlas_org = AtlasOrganization(org)
        projects = self.get_projects()
        atlas_org.add_projects(projects)
        for project in projects:
            clusters = self.get_clusters(project.id)
            atlas_org.add_clusters(project.id, clusters)
        return atlas_org

    """
    Projects
    """
    def get_one_project(self, project_id:str)->AtlasProject:
        org = self._atlas_api.get_one_project(project_id)
        return AtlasProject(org)

    def get_projects(self)->[AtlasProject, None, None]:
        result=[]
        projects = self._atlas_api.get_projects()
        for project in projects:
            result.append(AtlasProject(project))
        return result

    """
    Clusters
    """
    def get_one_cluster(self, project_id:str, cluster_name: str) -> AtlasCluster:
        cluster = self._atlas_api.get_one_cluster(project_id, cluster_name)
        return AtlasCluster(cluster)

    def get_clusters(self, project_id) -> [AtlasCluster, None, None]:
        result=[]
        clusters = self._atlas_api.get_clusters(project_id)
        for cluster in clusters:
            result.append(AtlasCluster(cluster))
        return result

    def pause_cluster(self, project_id:str, cluster_name:str):
        return self._atlas_api.pause(project_id, cluster_name)

    def resume_cluster(self, project_id:str, cluster_name:str):
        return self._atlas_api.resume(project_id, cluster_name)

    def __repr__(self):
        return f"OCPAPI(atlas_key={self._atlas_api.api_key})"
