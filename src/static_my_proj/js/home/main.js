
class CarouselTouchPlugin {
	/* 
		Permet de rajouter la navigation tactile pour le carousel
	*/
	constructor(carousel){
		/*
		* @param {Carousel} carousel


		*/
		carousel.container.addEventListener("dragstart", event => event.preventDefault())
		carousel.container.addEventListener("mousedown", this.startDrag.bind(this)) // L'écoute de l'évenement bougé de la souris
		carousel.container.addEventListener("touchstart", this.startDrag.bind(this)) // L'écoute de l'évenement bougé sur l'écran tactile
		window.addEventListener("mousemove", this.drag.bind(this))
		window.addEventListener("touchmove", this.drag.bind(this))

		window.addEventListener("touchend", this.endDrag.bind(this))
		window.addEventListener("mouseup", this.endDrag.bind(this))
		window.addEventListener("touchcancel", this.endDrag.bind(this))


		this.carousel = carousel 




	}


	startDrag (event) {
		// event.preventDefault()
		/*
			Demarrer le déplacement au touché

			@param{MouseEvent|TouchEvent}
		*/

		if(event.touches){
			if(event.touches.length>1){
				return
			} else{
				event = event.touches[0]
			}

		}


		this.origin = {x: event.screenX, y:event.screenY}
		this.width = this.carousel.containerWidth
		this.carousel.disableTransition()
		console.log("Start Drag")

	}



	drag (event){
		/*
			Déplacement
		*/


		if(this.origin){
			let point = event.touches ? event.touches[0] : event

			let translate = {x: point.screenX - this.origin.x, y: point.screenY - this.origin.y}
			if(event.touches && Math.abs(translate.x)> Math.abs(translate.y)){
				event.preventDefault()
				event.stopPropagation()
			}
			this.lastTranslate = translate
			let baseTranslate = this.carousel.currentItem * -100/ this.carousel.items.length 
			this.carousel.translate(baseTranslate + 100 * translate.x / this.width)
		}

	}



	endDrag(event){
		/*

		Find du défilement
		@param{MouseEvent|TouchEvent} event
		*/

		if(this.origin && this.lastTranslate){
			this.carousel.enableTransition()

			if(Math.abs(this.lastTranslate.x/ this.carousel.carouselWidth) > 0.2){
				if(this.lastTranslate.x <0){
					this.carousel.next()
				} else{
					this.carousel.prev()
				}
			} else{
				this.carousel.goToItem(this.carousel.currentItem)
			}



		}
		this.origin = null

	}


}



class Carousel {
	/*
	
	*This callback type is called requestCallback and is displayed as a global symbol

	* @callback moveCallback
	*@param (number) index


	* @param {HTMLElemnt} element
	* @param {object} options
	* @param {object} [options.slidesToScroll=1]: nombre d'élément à faire scroller
	* @param {object} [options.slidesVisible=1]: nombre d'élément à afficher dans un slide
	* @param {boolean} [options.loop=false]: doit-on boucler en fin de carousel ?
	* @param {boolean} [options.infinite=false]: 
	* @param {boolean} [options.pagination=false]:
	* @param {boolean} [options.navigation=true]:







	*/
	constructor (element, options={}){
		this.element = element
		// this.options = options // On pourrait directement assigner option à la propriété option mais ça risque de causer de soucis vu qu'elle est
									// optionelle si elle n'est pas définit lors de l'instanciation si on a pas de valeur pas des options ça peut endommager
		// Pour cela on assigne la métohode assign qui est disponible pour les objets
			this.options = Object.assign({}, {
				// Les élément par défaut ici si l'option est vide
				slidesToScroll:1,
				slidesVisible:1,
				loop: false,
				navigation:true,
				pagination: false,
				infinite:false,
			}, options)

			if(this.options.loop && this.options.infinite){
				throw new Error("Un carousel ne peut être à la fois en boucle et en infini")
			}

			let children = [].slice.call(element.children) //permet de prendre les enfant de element seulement pendant que le script est exécuter
			this.isMobile = false
			this.currentItem = 0
			this.moveCallbacks =  []
			this.offset = 0
			// Modification du DOM
			// Construction de la structure HTML du carousel
			this.root = this.createDivWithClass("carousel__ui")
			this.root.setAttribute("tabindex", "0")
			this.container = this.createDivWithClass("carousel__container")
			// On donne le container à root
			this.root.appendChild(this.container)

			// Dans notre element passer en paramètre du contrcuteur on donne root
			this.element.appendChild(this.root)

			this.items = children.map((child) =>{

				let item = this.createDivWithClass("carousel__item")
				item.appendChild(child)

				return item
			})

			if(this.options.infinite){

				this.offset = this.options.slidesVisible + this.options.slidesToScroll
				if(this.offset > children.length){
					console.error("Vous n'avez pas assez d'élément dans le carousel", element)
				}
				this.items = [ 
				...this.items.slice(this.items.length -  this.offset).map(item => item.cloneNode(true)),
				...this.items,
				...this.items.slice(0, this.offset).map(item => item.cloneNode(true)),
				]

				this.goToItem(this.offset, false)

			}


			this.items.forEach(item => this.container.appendChild(item))
			this.setStyle()

			if(this.options.navigation){
				console.log("navigation")
				this.createNavigation()
				}

			if(this.options.pagination){
			this.createPagination()
			}

			// Evenement
			this.moveCallbacks.forEach(cb => cb(this.currentItem))
			this.onWindowResize()

			window.addEventListener("resize", this.onWindowResize.bind(this))

			this.root.addEventListener("keyup", event => {
				if(event.key === "ArrowRight"|| event.key == "Right"){
					this.next()
				} else if(event.key === "ArrowLeft"|| event.key == "Left"){
					this.prev()

				}
			})



			if(this.options.infinite){

				this.container.addEventListener("transitionend", this.resetInfinite.bind(this))
			}



			new CarouselTouchPlugin(this)


	}



	setStyle (){
		// Applique les bonne dimensions aux éléments du carousel
		let ratio = this.items.length / this.slidesVisible
		this.container.style.width = (ratio * 100) + "%"
				
		this.items.forEach(item => item.style.width = ((100/this.slidesVisible)/ ratio) + "%")



		}


	createNavigation (){

		let nextButton = this.createDivWithClass("carousel__next")
		let prevButton = this.createDivWithClass("carousel__prev")
		this.root.appendChild(nextButton)
		this.root.appendChild(prevButton)

		nextButton.addEventListener("click", this.next.bind(this))
		prevButton.addEventListener("click", this.prev.bind(this))

		if(this.options.loop == true){
			return 
		}

		this.onMove(index=>{
			if(index===0){
				prevButton.classList.add("carousel__prev__hidden")
			}else{
				prevButton.classList.remove("carousel__prev__hidden")
			}

			if(this.items[this.currentItem + this.slidesVisible] === undefined){
				nextButton.classList.add("carousel__next__hidden")
			}else{
				nextButton.classList.remove("carousel__next__hidden")
			}
		})
	}

	createPagination (){
		/*
			*Crée de la pagination dans le DOM
		*/

		let pagination = this.createDivWithClass("carousel__pagination")
		let buttons = []
		this.root.appendChild(pagination)

		for(let i = 0; i<(this.items.length - 2 * this.offset); i= i + this.options.slidesToScroll){
			let button = this.createDivWithClass("carousel__pagination__button")
			button.addEventListener("click", (event) => this.goToItem(i + this.offset))
			pagination.appendChild(button)
			buttons.push(button)

		}

		this.onMove(index => {
			let count = this.items.length - 2 * this.offset
			let activeButton = buttons[Math.floor(((index - this.offset)%count) / this.options.slidesToScroll)]

			if(activeButton){
				buttons.forEach(button => button.classList.remove("carousel__pagination__button__active"))
				activeButton.classList.add("carousel__pagination__button__active")
			}
		})
	}


	translate (percent){

		this.container.style.transform = "translate3d(" + percent + "%,0,0)"	
	}


	next (){
		this.goToItem(this.currentItem + this.slidesToScroll)
	}

	prev (){
		this.goToItem(this.currentItem - this.slidesToScroll)
	}



	goToItem(index, animation=true){
		/*
			Deplace le carousel vers l'élément ciblé
			* @param(Number) index
			* @param(boolean) [animation=true]

		*/


		if(index < 0){
			if(this.options.loop){

				index = this.items.length - this.slidesToScroll
			} else{
				return
			}
		} else if (index >= this.items.length || (this.items[this.currentItem + this.slidesVisible]=== undefined && index > this.currentItem)){

			if(this.options.loop){

				index = 0
			} else{
				return 
			}
		}
		
		let translateX = index * -100/this.items.length
		if(animation === false){
			this.disableTransition()
		}
		this.translate(translateX)
		// this.container.style.transform = "translate3d(" + translateX + "%,0,0)"
		this.container.offsetHeight //Force repaint
		if(animation === false){
			//Redéfinition de l'animation à afficher
			this.enableTransition()
		}
		this.currentItem = index

		this.moveCallbacks.forEach(cb => cb(index))
	}


	resetInfinite (){
		/*
			Déplacer le container pour donner l'impression dd'un slide infini
		*/
		if(this.currentItem <= this.options.slidesToScroll){
			this.goToItem(this.currentItem + (this.items.length - 2 * this.offset), false)

		} else if(this.currentItem >= this.items.length - this.offset){
			this.goToItem(this.currentItem - (this.items.length - 2 * this.offset), false)
		}
	}
	/*
		@param(moveCallbacks)
	*/
	onMove(cb){
		this.moveCallbacks.push(cb)
	}


	onWindowResize (){
		let mobile = window.innerWidth <800
		if(mobile !== this.isMobile){
			this.isMobile = mobile
			this.setStyle()

			this.moveCallbacks.forEach(cb => cb(this.currentItem))

		}

	}
	
		/**
		*
		*@param (string) classsName
		*@returns HTMTElement
		*/
	createDivWithClass (className){
		/* 
		Méthode permettant la création d'un élément div avec la classe passer en paramètre
		*/

		let div = document.createElement("div")
		div.setAttribute("class", className)

		return div
	}

	disableTransition(){
		this.container.style.transition = "none"
	}

	enableTransition(){
		this.container.style.transition = ""
	}


	get slidesToScroll(){
		return this.isMobile ? 1 : this.options.slidesToScroll
	}

	get slidesVisible(){
		return this.isMobile ? 1 : this.options.slidesVisible
	}



	get containerWidth(){
		/*
			return{number}
		*/
		return this.container.offsetWidth
	}


	get carouselWidth(){
		/*

			*@return {number}
		*/
		return this.root.offsetWidth
	}

}






let onReady = function(){
		new Carousel(document.querySelector("#carousel__ui__2"),

		{	
			slidesVisible: 6,
			slidesToScroll:1,
			infinite: true,
			pagination:true,
	}
		)


	new Carousel(document.querySelector("#carousel__ui__3"),

		{	
			slidesVisible: 4,
			slidesToScroll:1,
			infinite: true,
			pagination:true,
	}
		)


	new Carousel(document.querySelector("#carousel__ui__electronique"),

		{	
			slidesVisible: 5,
			slidesToScroll:1,
			// infinite: true,
			// pagination:true,
	}
		)


	
	}

	if(document.readyState !== "loading"){
		onReady()
	}

//On attend que le contenu du DOM soit chargé
document.addEventListener("DOMContentLoaded", onReady)


