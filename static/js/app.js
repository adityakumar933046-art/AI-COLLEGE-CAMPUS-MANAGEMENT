// ====================================
// Smart Campus ERP
// ====================================

document.addEventListener("DOMContentLoaded",()=>{

    console.log("Smart Campus ERP Loaded");

});

// Scroll Top

const scrollBtn=document.getElementById("scrollTopBtn");

window.addEventListener("scroll",()=>{

    if(!scrollBtn) return;

    if(window.scrollY>300){

        scrollBtn.style.display="block";

    }

    else{

        scrollBtn.style.display="none";

    }

});

if(scrollBtn){

    scrollBtn.onclick=function(){

        window.scrollTo({

            top:0,

            behavior:"smooth"

        });

    }

}