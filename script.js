let menu = document.querySelector('#menu-icon');
let navbar = document.querySelector('.navbar');

menu.onclick= () => {
    menu.classList.toggle('bx-x');
    navbar.classList.tiggle('active');

}

window.onscroll= () => {
    menu.classList.remove('bx-x');
    navbar.classList.remove('active');
}

// typing text Code
const typed = new Typed('.multiple-text', {
    strings: ['Physical Fitness', 'Weight Gain','Strength Training','Fat Lose','weight Lifting','Running'],
    typeSpeed: 70,
    backSpeed: 60,
    baxkDelay: 1000,
    loop: true,
});

function calculateBMI() {

    let height = parseFloat(document.getElementById("height").value);
    let weight = parseFloat(document.getElementById("weight").value);

    const bmiValue = document.getElementById("bmiValue");
    const status = document.getElementById("status");
    const tip = document.getElementById("tip");
    const circle = document.getElementById("progressCircle");

    if (!height || !weight || height <= 0 || weight <= 0) {
        alert("Please enter valid Height and Weight");
        return;
    }

    // Height cm -> meter
    height = height / 100;

    // BMI
    let bmi = weight / (height * height);
    bmi = bmi.toFixed(1);

    // -------- Counter Animation --------
    let start = 0;
    let end = parseFloat(bmi);

    let counter = setInterval(() => {

        start += 0.2;

        bmiValue.innerHTML = start.toFixed(1);

        if (start >= end) {
            clearInterval(counter);
            bmiValue.innerHTML = bmi;
        }

    }, 20);

    // -------- Circle Animation --------

    const radius = 90;
    const circumference = 2 * Math.PI * radius;

    circle.style.strokeDasharray = circumference;

    let percent = Math.min(end, 40) / 40;

    let offset = circumference - (percent * circumference);

    circle.style.strokeDashoffset = offset;

    // -------- Status --------

    if (end < 18.5) {

        status.innerHTML = "🔵 Underweight";
        tip.innerHTML = "Increase your calorie intake and include more protein-rich foods in your diet.";

        circle.style.stroke = "#00BFFF";

    }

    else if (end < 25) {

        status.innerHTML = "🟢 Normal Weight";
        tip.innerHTML = "Excellent! Maintain your healthy lifestyle and continue regular exercise.";

        circle.style.stroke = "#45ffca";

    }

    else if (end < 30) {

        status.innerHTML = "🟠 Overweight";
        tip.innerHTML = "Add cardio workouts and maintain a balanced diet to improve your fitness.";

        circle.style.stroke = "#FFA500";

    }

    else {

        status.innerHTML = "🔴 Obese";
        tip.innerHTML = "Consult a fitness trainer and start with regular exercise and healthy eating.";

        circle.style.stroke = "#FF3B3B";

    }

}