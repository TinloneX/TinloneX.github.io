(function () {
      var leftPhotoImage = document.getElementById("left-photo-image");
      var rightPhotoImage = document.getElementById("right-photo-image");
      var treeImage = document.getElementById("sakura-tree-image");
      var petalsRoot = document.getElementById("petals");
      var petalCount = 40;

      function loadPreferredImage(imageElement) {
        if (!imageElement) {
          return;
        }

        var remoteSrc = imageElement.getAttribute("data-remote-src");
        var fallbackSrc = imageElement.getAttribute("data-fallback-src") || imageElement.getAttribute("src");

        if (!remoteSrc) {
          imageElement.src = fallbackSrc;
          return;
        }

        var remoteImage = new Image();
        var hasSettled = false;
        var fallbackTimer = window.setTimeout(function () {
          if (hasSettled) {
            return;
          }
          hasSettled = true;
          imageElement.src = fallbackSrc;
        }, 5000);

        remoteImage.onload = function () {
          if (hasSettled) {
            return;
          }
          hasSettled = true;
          window.clearTimeout(fallbackTimer);
          imageElement.src = remoteSrc;
        };

        remoteImage.onerror = function () {
          if (hasSettled) {
            return;
          }
          hasSettled = true;
          window.clearTimeout(fallbackTimer);
          imageElement.src = fallbackSrc;
        };

        remoteImage.src = remoteSrc;
      }

      loadPreferredImage(leftPhotoImage);
      loadPreferredImage(rightPhotoImage);
      loadPreferredImage(treeImage);

      for (var i = 0; i < petalCount; i += 1) {
        var petal = document.createElement("span");
        petal.className = "petal";
        petal.style.left = Math.random() * 100 + "%";
        petal.style.animationDelay = Math.random() * -18 + "s";
        petal.style.setProperty("--drift", (Math.random() * 220 - 110).toFixed(0) + "px");
        petal.style.setProperty("--fall-duration", (11 + Math.random() * 9).toFixed(2) + "s");
        petal.style.setProperty("--spin-duration", (3.4 + Math.random() * 3.6).toFixed(2) + "s");
        petal.style.setProperty("--petal-opacity", (0.5 + Math.random() * 0.32).toFixed(2));
        petal.style.setProperty("--petal-scale", (0.58 + Math.random() * 0.72).toFixed(2));
        petal.style.setProperty("--petal-size", (14 + Math.random() * 12).toFixed(0) + "px");
        petalsRoot.appendChild(petal);
      }
    }());
