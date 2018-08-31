	var menuShower = document.querySelector('#menu__shower') ;
	var menuListContainer = document.querySelector('.ui__2__menu__list') ;
	menuShower.addEventListener('click' , function (e) {
		e.preventDefault() ;
		menuListContainer.classList.toggle('show__menu__list') ;

	})




	var header = document.querySelector('.ui__1')

	window.addEventListener('scroll' , function () {
		var headerHeight = header.getBoundingClientRect().height ;
		var scrollY = window.scrollY ;
		console.log(headerHeight , scrollY) ;
		if (scrollY > headerHeight) {
			if (header.classList.contains('ui__fix__header')) { return ; }
			header.classList.add('ui__fix__header') ;
		}else {
			if (!header.classList.contains('ui__fix__header')) { return ; }
			header.classList.remove('ui__fix__header') 
		}
	})