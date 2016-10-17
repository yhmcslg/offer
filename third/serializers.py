from app001 import models
from rest_framework import serializers

class HostGroupSerializer(serializers.HyperlinkedModelSerializer):
    #Host = serializers.PrimaryKeyRelatedField(many=True, queryset=models.Host.objects.all())
    class Meta:
        model = models.HostGroup
        fields = ('url','groupname')

class HostStatusSerializer(serializers.HyperlinkedModelSerializer):
    #Host = serializers.PrimaryKeyRelatedField(many=True, queryset=models.Host.objects.all())
    class Meta:
        model = models.HostStatus
        fields = ('url','result_choices','name','memo')

class HostSerializer(serializers.HyperlinkedModelSerializer):
    #hostgroup = serializers.ReadOnlyField(source='models.HostGroup.groupname')
    #status = serializers.ReadOnlyField(source='models.HostStatus.name')
    class Meta:
        model = models.Host
        fields = ('url','hostname', 'lan_ip', 'wan_ip','status','hostgroup','memory','cpu','brand','os','create_at','update_at')
        #depth = 3
        
        
from django.contrib.auth.models import User, Group


class UserSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = User
        fields = ('url', 'username','password', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')        