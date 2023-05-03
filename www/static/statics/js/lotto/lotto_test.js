jQuery(function ($){
    $('.box a').click(function (e){
       $('.navichild, .bonus').stop();
       $('.navichild, .bonus').css("opacity", "0");
       $.ajax({
           url: getRandom,
           dataType: "json",
           success: makeNumberBalls,
           error: function (jpXHR, textStatus, errorThrown){
               console.log("error")
           }
       });
    });
});

function makeNumberBalls(reponse){
    /*1번 방법*/
    let results = reponse._result;
    let lottoResult = document.querySelector(".lotto-result");
    let child = lottoResult.firstChild
    if (child) {
        lottoResult.removeChild(child);
    }

    let div = document.createElement("div")
    lottoResult.append(div)

    for (let i = 0; i < results.length; i++) {
        let result = `<span>${results[i]}/</span>`;

        div.insertAdjacentHTML('beforeend', result);

    }

    /*또 다른 방법2*/
    let picks = reponse.pick;
    let pickResult = document.querySelector(".pick-result");
    let pickChild = pickResult.firstChild
    if (pickChild) {
        pickResult.removeChild(pickChild);
    }
    let pickDiv = document.createElement("div")
    pickResult.append(pickDiv)
    for (let i = 0; i < picks.length; i++) {
        let pick = `<span>${picks[i]}/</span>`;

        pickDiv.insertAdjacentHTML('beforeend', pick);

    }


}


