from django import forms


def validate_username_not_me(value):
    if value == 'me':
        raise forms.ValidationError(
            'не допустимо использовать имя me для username',
            params={'value': value},
        )
