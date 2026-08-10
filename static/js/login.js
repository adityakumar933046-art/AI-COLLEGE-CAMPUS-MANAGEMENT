const togglePassword=document.getElementById("togglePassword");
const password=document.getElementById("password");

if(togglePassword){

    togglePassword.addEventListener("click",function(){

        if(password.type==="password"){

            password.type="text";

            this.innerHTML='<i class="bi bi-eye-slash"></i>';

        }

        else{

            password.type="password";

            this.innerHTML='<i class="bi bi-eye"></i>';

        }

    });

}