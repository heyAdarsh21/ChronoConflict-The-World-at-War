document.addEventListener("DOMContentLoaded", () => {
    console.log("Project WW2 Loaded!");
    
    const mapImages = ["1939sept.jpg", "1939dec.jpg", "1940.jpg", "1941.jpg", "1942.jpg", "1943.jpg", "1944.jpg", "1945may.jpg", "1945aug.jpg", "1945sept.jpg"];
    
    let mapIndex = 0;
    function rotateMaps() {
        document.getElementById("war-map").src = mapImages[mapIndex];
        mapIndex = (mapIndex + 1) % mapImages.length;
    }

    setInterval(rotateMaps, 1000);
});

document.addEventListener("DOMContentLoaded", () => {
    document.body.style.opacity = 0;
    setTimeout(() => {
        document.body.style.opacity = 1;
    }, 300);
});

// fetch('history.txt')
//   .then(response => response.text())
//   .then(data => {
//       let formattedText = data.replace(/\n\n/g, '</p><p>').replace(/\n/g, '<br>');
//       formattedText = formattedText.replace(/## (.*?)/g, '<h2>$1</h2>');
//       formattedText = formattedText.replace(/!\[(.*?)\]\((.*?)\)/g, '<img src="$2" alt="$1">');
//       document.getElementById('articles').innerHTML = `<p>${formattedText}</p>`;
//   })
//   .catch(error => console.error('Error loading history:', error));


fetch('history.txt')
  .then(response => response.text())
  .then(data => {
      let formattedText = data.replace(/\n\n/g, '</p><p>').replace(/\n/g, '<br>');
      formattedText = formattedText.replace(/## (.*?)/g, '<h2>$1</h2>');
      formattedText = formattedText.replace(/!\[(.*?)\]\((.*?)\)/g, '<img src="$2" alt="$1">');
      
      document.getElementById("article-text").innerHTML = `<p>${formattedText}</p>`;
  })
  .catch(error => console.error('Error loading history:', error));


const articles = {
    backdrop: "<h2>Backdrop</h2><p>how it began</p>",
    politics: "<h2>Politics</h2><p>political scenario during war</p>",
    battles: "<h2>Battles</h2><p>key battles</p>",
    aftermath: "<h2>Aftermath</h2><p>aftermath of the war</p>",
    beginning: "<h2>Beginning</h2><p>here it begins...</p>",
    end: "<h2>End</h2><p>here it ends</p>",
    casualties: "<h2>Casualties</h2><p>casualties of war</p>",
    ideologies: "<h2>War of Ideologies</h2><p>the war of ideologies</p>"
};

function loadArticle(topic) {
    document.getElementById("articles").innerHTML = articles[topic];
}

let currentPage = 1;
const totalPages = 3;

function nextPage() {
    if (currentPage < totalPages) {
        document.getElementById(`page${currentPage}`).style.transform = "rotateY(-180deg)";
        currentPage++;
    }
}

function prevPage() {
    if (currentPage > 1) {
        currentPage--;
        document.getElementById(`page${currentPage}`).style.transform = "rotateY(0deg)";
    }
}
