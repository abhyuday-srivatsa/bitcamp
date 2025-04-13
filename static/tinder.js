likedCards = []

document.addEventListener('DOMContentLoaded', function () {
    matches = JSON.parse(localStorage.getItem('matches'));
    matches = [...new Set(matches)]
    NUM_CARDS = matches.length
    const cardPromises = [];
    let courseName = ""

    for (let i = 0; i <= NUM_CARDS; i++){
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
                
                if (course){
                    courseName = course['course_name']
                    if (courseName){
                        courseDescription = course['course_description']
                        allProfs = []
                        sections = course['sections']
                        sections.forEach((section, i) => {
                            profs = section['professor(s)']

                            allProfs = allProfs.concat(profs)
                            allProfs.sort()
                            
                        });

                        allProfs = [...new Set(allProfs)]
                        let professorOptions = allProfs.map(prof => {
                            return `<option value="${prof}">${prof}</option>`;
                        }).join("");

                        var newCard = document.createElement('div');
                        newCard.classList.add('tinder--card');
                        newCard.innerHTML = `
        <div class="prof--dropdown">
            <label for="profs"></label>
            <select name="profs" id="profs">
                <option value="0">Select Professor</option>
                ${professorOptions}
            </select>
        </div>

        <div class="grade-distribution">
            <canvas id="gradeChart-${i}"></canvas>
        </div>

        <div class="course-name">
            <h3>${courseName}</h3>
        </div>

        <div class="course-description">
            <p>${courseDescription}</p>
        </div>
        `;
                        document.querySelector('.tinder--cards').appendChild(newCard);
                        
                        const dropdown = newCard.querySelector('select[name="profs"]');
                        console.log(courseName)
                        const ID = courseName.slice(0, 7);
                        dropdown.addEventListener('change', function () {
                            const selectedProfessor = this.value;
                            newCard.setAttribute('data-selected-professor', selectedProfessor);
                            fetch('/get_grades', {
                                method: 'POST',
                                headers: {
                                'Content-Type': 'application/json'
                                },
                                body: JSON.stringify({ 
                                    professor: selectedProfessor,
                                    courseID: ID
                                })
                            })
                            .then(response => response.json())
                            .then(data => {
                                
                                const grades = data.response;
                                if (grades['avg_grade']){
                                    const desiredGradeOrder = [
                                        "A+", "A", "A-",
                                        "B+", "B", "B-",
                                        "C+", "C", "C-",
                                        "D+", "D", "D-",
                                        "F", "W", "Other"
                                        ];
                                    const gradeTotals = grades.grade_totals;

                                    const gradeLabels = desiredGradeOrder.filter(grade => grade in gradeTotals);
                                    const gradeValues = gradeLabels.map(label => gradeTotals[label]);

                                    // Create the chart
                                    const canvasId = `gradeChart-${i}`;
                                    const ctx = document.getElementById(canvasId).getContext('2d');

                                    if(Chart.getChart(ctx)) {
                                        Chart.getChart(ctx)?.destroy()
                                    }

                                    const gradeChart = new Chart(ctx, {
                                        type: 'bar',
                                        data: {
                                            labels: gradeLabels,  // X-axis labels (grade types)
                                            datasets: [{
                                                label: 'Grade Distribution',
                                                data: gradeValues,  // Y-axis data (frequency of each grade)
                                                backgroundColor: '#4CAF50',  // Color for the bars
                                                borderColor: '#388E3C',
                                                borderWidth: 1
                                            }]
                                        },
                                        options: {
                                            responsive: true,
                                            scales: {
                                                y: {
                                                    beginAtZero: true,  // Ensure the Y-axis starts at zero
                                                    title: {
                                                        display: true,
                                                        text: 'Frequency'
                                                    }
                                                },
                                                x: {
                                                    title: {
                                                        display: true,
                                                        text: 'Grade'
                                                    }
                                                }
                                            }
                                        }
                                    });
                                }
                                
                            })
                            .catch(error => {
                                console.error('Error fetching grades:', error);
                            });
                        });
                    }
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
                        const selectedProf = event.target.getAttribute('data-selected-professor') || null;
                        const courseID = event.target.querySelector('.course-name h3')?.textContent?.slice(0, 7);
                        likedCards.push([courseID,selectedProf]);
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
                    checkIfFinished();
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
                    const selectedProf = card.getAttribute('data-selected-professor') || null;
                    const courseID = card.querySelector('.course-name h3')?.textContent?.slice(0, 7);
                    likedCards.push([courseID,selectedProf]);
                
                    card.style.transform = 'translate(' + moveOutWidth + 'px, -100px) rotate(-30deg)';
                } else {
                    card.style.transform = 'translate(-' + moveOutWidth + 'px, -100px) rotate(30deg)';
                }

                initCards();
                checkIfFinished();
                event.preventDefault();
            };
        }

        var nopeListener = createButtonListener(false);
        var loveListener = createButtonListener(true);

        nope.addEventListener('click', nopeListener);
        love.addEventListener('click', loveListener);
    });
});

function checkIfFinished() {
    const remainingCards = document.querySelectorAll('.tinder--card:not(.removed)');
    if (remainingCards.length === 0) {
        // All cards have been swiped
        console.log(likedCards)
        fetch('/generate_schedule', {
            method: 'POST', 
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({input : likedCards})
        })
        .then(response => {
            if (response.redirected) {
                window.location.href = response.url
            }
        })
        
    }
}

