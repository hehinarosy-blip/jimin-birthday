const menuButton =
    document.getElementById("menuButton");

const mainNav =
    document.getElementById("mainNav");


menuButton.addEventListener("click", () => {

    mainNav.classList.toggle("open");

});


document
    .querySelectorAll("#mainNav a")
    .forEach(link => {

        link.addEventListener("click", () => {

            mainNav.classList.remove("open");

        });

    });



const openWish =
    document.getElementById("openWish");

const wishModal =
    document.getElementById("wishModal");

const closeWish =
    document.getElementById("closeWish");

const closeWishButton =
    document.getElementById("closeWishButton");

const wishForm =
    document.getElementById("wishForm");

const wishInput =
    document.getElementById("wishInput");

const characterCount =
    document.getElementById("characterCount");

const wishSky =
    document.getElementById("wishSky");

const wishCount =
    document.getElementById("wishCount");


const STORAGE_KEY =
    "jiminAfricanArmyWishes";

const MIGRATION_KEY =
    `${STORAGE_KEY}SharedMigration`;


openWish.addEventListener("click", () => {

    wishModal.classList.add("active");

    setTimeout(() => {

        wishInput.focus();

    }, 150);

});


function closeWishWindow() {

    wishModal.classList.remove("active");

}


closeWish.addEventListener(
    "click",
    closeWishWindow
);


closeWishButton.addEventListener(
    "click",
    closeWishWindow
);


document.addEventListener(
    "keydown",
    event => {

        if (event.key === "Escape") {

            closeWishWindow();

        }

    }
);



wishInput.addEventListener(
    "input",
    () => {

        characterCount.textContent =
            wishInput.value.length;

    }
);



function getLegacyWishes() {

    try {

        return JSON.parse(
            localStorage.getItem(STORAGE_KEY)
        )?.filter(wish => typeof wish === "string") || [];

    } catch (error) {

        return [];

    }

}



async function requestWishes(options = {}) {

    const response = await fetch("/api/wishes", options);

    if (!response.ok) {

        throw new Error("Unable to load shared messages.");

    }

    const wishes = await response.json();

    return Array.isArray(wishes)
        ? wishes.filter(wish => typeof wish === "string")
        : [];

}



function createWish(
    text,
    index
) {

    const wish =
        document.createElement("div");


    wish.className =
        "wish-item";


    wish.textContent =
        text;


    const positions = [

        { left: "4%", top: "12%" },
        { left: "28%", top: "8%" },
        { left: "63%", top: "10%" },
        { left: "78%", top: "27%" },
        { left: "5%", top: "42%" },
        { left: "27%", top: "68%" },
        { left: "62%", top: "72%" },
        { left: "80%", top: "53%" },
        { left: "17%", top: "52%" },
        { left: "45%", top: "20%" },
        { left: "48%", top: "81%" },
        { left: "72%", top: "78%" },
        { left: "12%", top: "30%" },
        { left: "36%", top: "34%" },
        { left: "58%", top: "45%" },
        { left: "68%", top: "58%" },
        { left: "18%", top: "76%" },
        { left: "49%", top: "60%" },
        { left: "71%", top: "42%" },
        { left: "83%", top: "69%" },
        { left: "9%", top: "58%" },
        { left: "33%", top: "54%" },
        { left: "51%", top: "24%" },
        { left: "88%", top: "12%" }

    ];


    const getPosition = (positionIndex) => {

        if (positionIndex < positions.length) {

            return positions[positionIndex];

        }

        const column = positionIndex % 5;
        const row = Math.floor(positionIndex / 5) % 6;

        const left = 8 + column * 18 + (positionIndex % 2) * 4;
        const top = 10 + row * 14 + (positionIndex % 3) * 3;

        return {
            left: `${Math.min(left, 88)}%`,
            top: `${Math.min(top, 82)}%`
        };

    };


    const position = getPosition(index);


    wish.style.left =
        position.left;


    wish.style.top =
        position.top;


    const rotations = [
        -2,
        1,
        -1,
        2,
        -3,
        2
    ];


    wish.style.transform =
        `rotate(${rotations[
            index % rotations.length
        ]}deg)`;


    return wish;

}



function renderWishes(wishes) {

    document
        .querySelectorAll(".wish-item")
        .forEach(item => {

            item.remove();

        });


    [...wishes]
        .reverse()
        .forEach(
            (wish, index) => {

                wishSky.appendChild(
                    createWish(
                        wish,
                        index
                    )
                );

            }
        );


    wishCount.textContent =
        wishes.length;

}


async function loadWishes() {

    let wishes = await requestWishes();

    if (localStorage.getItem(MIGRATION_KEY) !== "true") {

        const legacyWishes = getLegacyWishes();

        if (legacyWishes.length) {

            wishes = await requestWishes({
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ wishes: legacyWishes })
            });

        }

        localStorage.setItem(MIGRATION_KEY, "true");

    }

    renderWishes(wishes);

}



wishForm.addEventListener(
    "submit",
    async event => {

        event.preventDefault();


        const text =
            wishInput.value.trim();


        if (!text) {

            return;

        }


        const submitButton =
            wishForm.querySelector("button[type='submit']");

        submitButton.disabled = true;

        try {

            const wishes = await requestWishes({
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ text })
            });

            wishInput.value = "";
            characterCount.textContent = "0";
            wishStatus.textContent = "";
            closeWishWindow();
            renderWishes(wishes);

        } catch (error) {

            wishStatus.textContent =
                "Could not share your message. Please try again.";

        } finally {

            submitButton.disabled = false;

        }

    }
);



const voiceAudio =
    document.getElementById("voiceAudio");

const audioPlay =
    document.getElementById("audioPlay");

const audioStatus =
    document.getElementById("audioStatus");


audioPlay.addEventListener(
    "click",
    () => {

        if (voiceAudio.paused) {

            voiceAudio
                .play()
                .then(() => {

                    audioPlay.textContent =
                        "❚❚";

                    audioStatus.textContent =
                        "Playing the message...";

                })
                .catch(() => {

                    audioStatus.textContent =
                        "Please add your recording to assets/";

                });

        } else {

            voiceAudio.pause();

            audioPlay.textContent =
                "▶";

            audioStatus.textContent =
                "Paused.";

        }

    }
);



voiceAudio.addEventListener(
    "ended",
    () => {

        audioPlay.textContent =
            "▶";

        audioStatus.textContent =
            "Message finished. 💙";

    }
);



const wishStatus =
    document.getElementById("wishStatus");


loadWishes().catch(() => {

    wishStatus.textContent =
        "Messages could not be loaded. Please try again later.";

});


window.setInterval(() => {

    if (!document.hidden) {

        requestWishes()
            .then(renderWishes)
            .catch(() => {});

    }

}, 15000);


window.addEventListener("focus", () => {

    requestWishes()
        .then(renderWishes)
        .catch(() => {});

});