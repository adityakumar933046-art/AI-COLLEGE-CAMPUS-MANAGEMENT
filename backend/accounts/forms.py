from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import User


# ==========================================================
# LOGIN FORM
# ==========================================================

class LoginForm(forms.Form):

    username = forms.CharField(

        max_length=150,

        widget=forms.TextInput(

            attrs={

                "class": "form-control",

                "placeholder": "Email or User ID",

                "autocomplete": "username",

            }

        ),

    )

    password = forms.CharField(

        widget=forms.PasswordInput(

            attrs={

                "class": "form-control",

                "placeholder": "Password",

                "autocomplete": "current-password",

            }

        ),

    )

    remember_me = forms.BooleanField(

        required=False,

        initial=False,

    )

    def __init__(self, *args, **kwargs):

        self.request = kwargs.pop("request", None)

        super().__init__(*args, **kwargs)

    def clean(self):

        cleaned_data = super().clean()

        login_id = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if login_id and password:

            # Email login
            if "@" in login_id:

                try:

                    user_obj = User.objects.get(
                        email__iexact=login_id
                    )

                    username = user_obj.username

                except User.DoesNotExist:

                    username = login_id

            else:

                username = login_id

            user = authenticate(

                request=self.request,

                username=username,

                password=password,

            )

            if user is None:

                raise ValidationError(
                    "Invalid Email/User ID or Password."
                )

            if not user.is_active:

                raise ValidationError(
                    "Your account is inactive."
                )

            cleaned_data["user"] = user

        return cleaned_data
    
    # ==========================================================
# REGISTER FORM
# ==========================================================

class RegisterForm(forms.ModelForm):

    password = forms.CharField(

        label="Password",

        widget=forms.PasswordInput(

            attrs={

                "class": "form-control",

                "placeholder": "Password",

            }

        ),

    )

    confirm_password = forms.CharField(

        label="Confirm Password",

        widget=forms.PasswordInput(

            attrs={

                "class": "form-control",

                "placeholder": "Confirm Password",

            }

        ),

    )

    class Meta:

        model = User

        fields = (

            "username",

            "first_name",

            "last_name",

            "email",

            "phone",

            "role",

            "password",

            "confirm_password",

        )

        widgets = {

            "username": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "first_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "last_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "email": forms.EmailInput(
                attrs={"class": "form-control"}
            ),

            "phone": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "role": forms.Select(
                attrs={"class": "form-select"}
            ),

        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["role"].choices = [

            (User.Roles.STUDENT, "Student"),

            (User.Roles.TEACHER, "Teacher"),

        ]

    def clean_username(self):

        username = self.cleaned_data.get("username")

        if User.objects.filter(
            username__iexact=username
        ).exists():

            raise ValidationError(
                "Username already exists."
            )

        return username

    def clean_email(self):

        email = self.cleaned_data.get("email")

        if User.objects.filter(
            email__iexact=email
        ).exists():

            raise ValidationError(
                "Email already exists."
            )

        return email

    def clean_phone(self):

        phone = self.cleaned_data.get("phone")

        if phone:

            if not phone.isdigit():

                raise ValidationError(
                    "Phone number must contain only digits."
                )

            if len(phone) != 10:

                raise ValidationError(
                    "Phone number must be exactly 10 digits."
                )

        return phone

    def clean_password(self):

        password = self.cleaned_data.get("password")

        validate_password(password)

        return password

    def clean(self):

        cleaned_data = super().clean()

        password = cleaned_data.get("password")

        confirm_password = cleaned_data.get(
            "confirm_password"
        )

        if password and confirm_password:

            if password != confirm_password:

                raise ValidationError(
                    "Passwords do not match."
                )

        return cleaned_data

    def save(self, commit=True):

        user = super().save(commit=False)

        user.set_password(
            self.cleaned_data["password"]
        )

        user.is_verified = False

        if commit:

            user.save()


        return user
    
    # ==========================================================
# USER UPDATE FORM
# ==========================================================

class UserUpdateForm(forms.ModelForm):

    class Meta:

        model = User

        fields = [

            "first_name",

            "last_name",

            "email",

            "phone",

            "date_of_birth",

            "gender",

            "address",

            "role",

            "is_active",

            "is_verified",

        ]

        widgets = {

            "first_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "last_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "email": forms.EmailInput(
                attrs={"class": "form-control"}
            ),

            "phone": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "date_of_birth": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "gender": forms.Select(
                attrs={"class": "form-select"}
            ),

            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),

            "role": forms.Select(
                attrs={"class": "form-select"}
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),

            "is_verified": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),

        }

    def clean_email(self):

        email = self.cleaned_data.get("email")

        if User.objects.exclude(
            pk=self.instance.pk
        ).filter(
            email__iexact=email
        ).exists():

            raise ValidationError(
                "Email already exists."
            )

        return email

    def clean_phone(self):

        phone = self.cleaned_data.get("phone")

        if phone:

            if not phone.isdigit():

                raise ValidationError(
                    "Phone number must contain only digits."
                )

            if len(phone) != 10:

                raise ValidationError(
                    "Phone number must be exactly 10 digits."
                )

        return phone
    
    # ==========================================================
# PROFILE UPDATE FORM
# ==========================================================

# ==========================================================
# PHASE 7 — ROLE-AWARE SECURE PROFILE UPDATE FORM
# ==========================================================

class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "First Name"}),
    )
    last_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Last Name"}),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email Address"}),
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone Number"}),
    )
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )
    gender = forms.ChoiceField(
        choices=[("", "Select Gender"), ("MALE", "Male"), ("FEMALE", "Female"), ("OTHER", "Other")],
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Address"}),
    )
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone", "date_of_birth", "gender", "address", "profile_picture"]

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if not email:
            raise ValidationError("Email address cannot be empty.")
        query = User.objects.filter(email__iexact=email)
        if self.instance and self.instance.pk:
            query = query.exclude(pk=self.instance.pk)
        if query.exists():
            raise ValidationError("This email address is already in use by another account.")
        return email

    def clean_profile_picture(self):
        picture = self.cleaned_data.get("profile_picture")
        if picture:
            valid_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
            ext = os.path.splitext(picture.name)[1].lower()
            if ext not in valid_extensions:
                raise ValidationError("Unsupported image format. Allowed formats: JPG, PNG, GIF, WEBP.")
            if picture.size > 5 * 1024 * 1024:
                raise ValidationError("Profile picture size cannot exceed 5 MB.")
        return picture

# ==========================================================
# FORGOT PASSWORD FORM
# ==========================================================

class ForgotPasswordForm(forms.Form):

    email = forms.EmailField(

        widget=forms.EmailInput(

            attrs={

                "class": "form-control",

                "placeholder": "Enter your registered email",

            }

        )

    )

    def clean_email(self):

        email = self.cleaned_data.get("email")

        try:

            User.objects.get(email__iexact=email)

        except User.DoesNotExist:

            raise ValidationError(
                "No account found with this email."
            )

        return email


# ==========================================================
# OTP VERIFICATION FORM
# ==========================================================

class OTPVerificationForm(forms.Form):

    otp = forms.CharField(

        max_length=6,

        min_length=6,

        widget=forms.TextInput(

            attrs={

                "class": "form-control",

                "placeholder": "Enter 6 Digit OTP",

                "maxlength": "6",

            }

        ),

    )

    def clean_otp(self):

        otp = self.cleaned_data.get("otp")

        if not otp.isdigit():

            raise ValidationError(
                "OTP must contain only digits."
            )

        if len(otp) != 6:

            raise ValidationError(
                "OTP must be exactly 6 digits."
            )

        return otp
    
    # ==========================================================
# RESET PASSWORD FORM
# ==========================================================

class ResetPasswordForm(forms.Form):

    new_password = forms.CharField(

        label="New Password",

        widget=forms.PasswordInput(

            attrs={

                "class": "form-control",

                "placeholder": "Enter New Password",

            }

        ),

    )

    confirm_password = forms.CharField(

        label="Confirm Password",

        widget=forms.PasswordInput(

            attrs={

                "class": "form-control",

                "placeholder": "Confirm New Password",

            }

        ),

    )

    def clean_new_password(self):

        password = self.cleaned_data.get("new_password")

        validate_password(password)

        return password

    def clean(self):

        cleaned_data = super().clean()

        password = cleaned_data.get("new_password")

        confirm = cleaned_data.get("confirm_password")

        if password and confirm:

            if password != confirm:

                raise ValidationError(
                    "Passwords do not match."
                )

        return cleaned_data


# ==========================================================
# CHANGE PASSWORD FORM
# ==========================================================

class CustomPasswordChangeForm(PasswordChangeForm):

    old_password = forms.CharField(

        widget=forms.PasswordInput(

            attrs={

                "class": "form-control",

                "placeholder": "Current Password",

            }

        )

    )

    new_password1 = forms.CharField(

        widget=forms.PasswordInput(

            attrs={

                "class": "form-control",

                "placeholder": "New Password",

            }

        )

    )

    new_password2 = forms.CharField(

        widget=forms.PasswordInput(

            attrs={

                "class": "form-control",

                "placeholder": "Confirm New Password",

            }

        )

    )