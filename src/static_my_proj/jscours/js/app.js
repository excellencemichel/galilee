

var getHtppRequest = function(httpRequest){

var httpRequest = false
if(window.XMLHttpRequest){
	httpRequest = new XMLHttpRequest()
	if(httpRequest.overrideMineType){
		httpRequest.overrideMineType("text/xml")
	}
} else if(window.ActiveXObject){
	try{
		httpRequest = new ActiveXObject("Msxml2.XMLHTTP")
	}
	catch(e){
		try{
			httpRequest = new ActiveXObject("Microsoft.XMLHTTP")
		}
		catch(e){
			console.log(e)
		}
	}
}

if(!httpRequest){
	alert("Abondon !(Impossible de créer une instance XMLHTTP")
	return false
}

return httpRequest
}



var links = document.querySelectorAll(".meteo")
var resultat = document.getElementById('resultat')


for(var i= 0; i< links.length; i++ ){
	link = links[i]
	link.addEventListener("click", function(event){
		event.preventDefault()
		resultat.innerHTML ="Chargement..."
		var httpRequest = getHtppRequest()

		httpRequest.onreadystatechange = function(){
			if(httpRequest.readyState === 4){
				var texte = httpRequest.responseText
				resultat.innerHTML=texte
			}
		}

		httpRequest.open("GET", this.getAttribute("href"), true)

		httpRequest.send()
	})
}



var resultat1 = document.querySelector("#resultat1")
var form = document.querySelector("#form")

form.addEventListener("submit", function(event){
	event.preventDefault()
	resultat1.innerHTML = "Chargement... de la search"
	var httpRequest1 = getHtppRequest()
	httpRequest1.onreadystatechange = function(){
		if(httpRequest1.readyState===4){
			resultat1.innerHTML = ""
		
		if(httpRequest1.status==200){
			resultat1.innerHTML = getHtppRequest.responseText
		} else{
			alert("Impossible de se connecter au serveur pour le formulaire")
		}

	}
	}

	httpRequest1.open("POST", "/jscours/testajax", true)
	var data = new FormData()

	// var input = document.querySelector("#q")
	// data.append("q", input.value )

	httpRequest1.send(data)

})