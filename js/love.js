(function () {
      var start = new Date(2025, 0, 30, 15, 48, 0).getTime();
      var daysEl = document.getElementById("days");
      var hoursEl = document.getElementById("hours");
      var minutesEl = document.getElementById("minutes");
      var secondsEl = document.getElementById("seconds");
      var totalSecondsEl = document.getElementById("total-seconds");
      var leftPhotoImage = document.getElementById("left-photo-image");
      var rightPhotoImage = document.getElementById("right-photo-image");

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

      function pad(num) {
        return String(num).padStart(2, "0");
      }

      function tick() {
        var now = Date.now();
        var diff = Math.max(0, now - start);
        var totalSeconds = Math.floor(diff / 1000);
        var days = Math.floor(totalSeconds / 86400);
        var hours = Math.floor((totalSeconds % 86400) / 3600);
        var minutes = Math.floor((totalSeconds % 3600) / 60);
        var seconds = totalSeconds % 60;

        daysEl.textContent = days;
        hoursEl.textContent = pad(hours);
        minutesEl.textContent = pad(minutes);
        secondsEl.textContent = pad(seconds);
        totalSecondsEl.textContent = totalSeconds.toLocaleString("zh-CN");
      }

      loadPreferredImage(leftPhotoImage);
      loadPreferredImage(rightPhotoImage);
      tick();
      window.setInterval(tick, 1000);
    })();
