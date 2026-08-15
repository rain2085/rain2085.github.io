var ele;
const raw = "tempest799165387";

function getContent(date){
  if(Date.now()>Date.parse(date)){
    return raw;
  }
  else{
    return raw.replace(/./g, '*');
  }
}

const contactInfo = getContent("2026-8-15 22:38:00");

document.addEventListener("DOMContentLoaded",()=>{
    ele = document.querySelector("#contactInfo");
    ele.innerText = contactInfo;
})

function showContent(){
    ele.innerText = raw;
}

function hideContent(){
    ele.innerText = raw.replace(/./g, "*");
}
