from rest_framework import permissions

#自定义一个权限
class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):  #obj就是数据表中的model
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:      #如果是安全的方式就直接返回Ture否则就判断user
            return True

        # Instance must have an attribute named `owner`.
        return obj.user == request.user                   #判断model取出的model和当前request.user是否是相同