var text;

function sclicked(){
    const h2 = document.querySelector("h2");
    text = h2.innerText;
    h2.innerText = "tempest799165387";
}

function hclicked(){
    const h2 = document.querySelector("h2");
    h2.innerText = text;
}
