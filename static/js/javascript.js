

let contador = 
function conteo() {
    contador ++;
    document.querySelector("h1").innerHTML = contador;

    if (contador % 10 === 0) {
        alert(`Conteo es ahora ${contador}`)
    }
}

document.addEventListener("DOMContentLoader", function() {
    document.querySelector("select").onchange = function () {
        document.querySelector("#hola").style.color = Selection.value
    }
});

