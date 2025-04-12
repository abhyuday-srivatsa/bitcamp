document.addEventListener('DOMContentLoaded', function () {
    const matches = JSON.parse(localStorage.getItem('matches'));
    console.log(matches)
    NUM_CARDS = matches.length
    const likedCards = [];
    const cardPromises = [];


    for (let i = 0; i < NUM_CARDS; i++){
        if (matches[i]){
            const promise = fetch('/get_courses', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({input : matches[i]})
            })
            .then(response => response.json())
            .then(data => {
                const course = data.response;
                
                courseName = course['course_name']
                courseDescription = course['course_description']
                if (courseName){
                    console.log("CREATED CARD FOR ", courseName)
                    var newCard = document.createElement('div');
                    newCard.classList.add('tinder--card');
                    newCard.innerHTML = `<h3>${courseName}</h3><p>${courseDescription}</p>`;
                
                    document.querySelector('.tinder--cards').appendChild(newCard);
                }
            });
            cardPromises.push(promise);
        }
    }
    Promise.all(cardPromises).then(() => {
        var tinderContainer = document.querySelector('.tinder');
        var allCards = document.querySelectorAll('.tinder--card');
        var nope = document.getElementById('nope');
        var love = document.getElementById('love');

        function initCards() {
            var newCards = document.querySelectorAll('.tinder--card:not(.removed)');
        
            newCards.forEach(function (card, index) {
                card.style.zIndex = newCards.length - index;
                card.style.transform = 'scale(' + (20 - index) / 20 + ') translateY(-' + 30 * index + 'px)';
                card.style.opacity = (10 - index) / 10;
            });
        
            tinderContainer.classList.add('loaded');
        }

        initCards();    

        allCards.forEach(function (el) {
            var hammertime = new Hammer(el);

            hammertime.on('pan', function (event) {
                el.classList.add('moving');
            });

            hammertime.on('pan', function (event) {
                if (event.deltaX === 0) return;
                if (event.center.x === 0 && event.center.y === 0) return;

                tinderContainer.classList.toggle('tinder_love', event.deltaX > 0);
                tinderContainer.classList.toggle('tinder_nope', event.deltaX < 0);

                var xMulti = event.deltaX * 0.03;
                var yMulti = event.deltaY / 80;
                var rotate = xMulti * yMulti;

                event.target.style.transform = 'translate(' + event.deltaX + 'px, ' + event.deltaY + 'px) rotate(' + rotate + 'deg)';
            });

            hammertime.on('panend', function (event) {
                el.classList.remove('moving');
                tinderContainer.classList.remove('tinder_love');
                tinderContainer.classList.remove('tinder_nope');

                var moveOutWidth = document.body.clientWidth;
                var keep = Math.abs(event.deltaX) < 80 || Math.abs(event.velocityX) < 0.5;

                event.target.classList.toggle('removed', !keep);

                if (keep) {
                    event.target.style.transform = '';
                } else {
                    if (event.deltaX > 0) {
                        // Save right swipe
                        likedCards.push(event.target.innerHTML);
                    }
                    var endX = Math.max(Math.abs(event.velocityX) * moveOutWidth, moveOutWidth);
                    var toX = event.deltaX > 0 ? endX : -endX;
                    var endY = Math.abs(event.velocityY) * moveOutWidth;
                    var toY = event.deltaY > 0 ? endY : -endY;
                    var xMulti = event.deltaX * 0.03;
                    var yMulti = event.deltaY / 80;
                    var rotate = xMulti * yMulti;

                    event.target.style.transform = 'translate(' + toX + 'px, ' + (toY + event.deltaY) + 'px) rotate(' + rotate + 'deg)';
                    initCards();
                }
            });
        });

        function createButtonListener(love) {
            return function (event) {
                var cards = document.querySelectorAll('.tinder--card:not(.removed)');
                var moveOutWidth = document.body.clientWidth * 1.5;

                if (!cards.length) return false;

                var card = cards[0];

                card.classList.add('removed');

                if (love) {
                    likedCards.push(card.innerHTML)
                    card.style.transform = 'translate(' + moveOutWidth + 'px, -100px) rotate(-30deg)';
                } else {
                    card.style.transform = 'translate(-' + moveOutWidth + 'px, -100px) rotate(30deg)';
                }

                initCards();

                event.preventDefault();
            };
        }

        var nopeListener = createButtonListener(false);
        var loveListener = createButtonListener(true);

        nope.addEventListener('click', nopeListener);
        love.addEventListener('click', loveListener);
    });
});