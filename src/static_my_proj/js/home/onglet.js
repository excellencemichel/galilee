

(function(){

var afficherOnglet = function(a, animations){
		if(animations === undefined){
			animations = true
		}
		var li = a.parentNode
		var div = a.parentNode.parentNode.parentNode
		var aAfficher = div.querySelector(a.getAttribute("href"))
		var activeTab = div.querySelector(".tab-content.active")

		//On verifie est-ce que l'élément sur lequel on veut retirer la classe active n'est pas celle qui a la classe
		if(li.classList.contains("active")){
			// Si c'est le cas l'exécution de la fonction s'arrête là et on retourne false
			console.log("C'est lui qui a")
			return false
		}

		//Dans le cas contraire on continu l'exécution
		//On retir la classe active de l'ongle qui est actif
		div.querySelector(".tabs .active").classList.remove("active")

		//On ajoute la classe active à l'élément qui a été siblé par l'évenement écouté en l'ocurrence click
		li.classList.add("active")

		//On retire la classe active sur le contenu
		//div.querySelector(".tab-content.active").classList.remove("active")

		//On ajoute la classe active au contenu correspondant au clic
		//div.querySelector(a.getAttribute("href")).classList.add("active")

		//On ajoute la classe fade pour l'élément actif
		// A la fin de l'animation
			//On retire la classe fade et active
			// On ajoute la classe active et fade à l'élement à afficher
			// On ajoute la classe in
			if(animations){
				activeTab.classList.add("fade")
			activeTab.classList.remove("in")
			var transitionend = function(event){
				this.classList.remove("fade")
				this.classList.remove("active")

				aAfficher.classList.add("active")
				aAfficher.classList.add("fade")
				aAfficher.offsetWidth
				aAfficher.classList.add("in")
				activeTab.removeEventListener("transitionend", transitionend)

				


			}
				activeTab.removeEventListener("transitionend", transitionend)
				activeTab.removeEventListener("webkitTransitionend", transitionend)
				activeTab.removeEventListener("oTransitionend", transitionend)
			//On reste à l'écoute de la fin de la transition CSS
			activeTab.addEventListener("transitionend", transitionend)
		}else{
			aAfficher.classList.add("active")
			activeTab.classList.remove("active")
		}
			

}


var tabs = document.querySelectorAll(".tabs a")

for(var i = 0; i<tabs.length; i++){
	tabs[i].addEventListener("click", function(event){
		event.preventDefault()
		afficherOnglet(this)
		


	})
}

})()