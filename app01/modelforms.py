from app01 import models
from django.forms import ModelForm

class My_model(ModelForm):
    class Meta:
        model=models.UserInfo
        fields='__all__'
        from django.forms import widgets as wid
        widgets={
            'name':wid.TextInput(attrs={'class':'form-control'}),
            'pwd':wid.PasswordInput(attrs={'class':'form-control'}),
            'is_book':wid.NullBooleanSelect(attrs={'class':'form-control'})
        }
        labels={
            'name':'用户名',
            'pwd':'密码',
            'is_book':'预订权限'
        }

