document.addEventListener('DOMContentLoaded', () => {
    const comparisonContainers = document.querySelectorAll('.video-comparison');

  comparisonContainers.forEach((comparisonContainer) => {    
    // const comparisonContainer = document.querySelector('.video-comparison');
    const beforeVideo = comparisonContainer.querySelector('.before');
    const afterVideo = comparisonContainer.querySelector('.after');
    const divider = comparisonContainer.querySelector('.divider');
    const seekSlider = comparisonContainer.querySelector('input[type="range"]');
    const togglePlayButton = comparisonContainer.querySelector('.video-playbutton');
    const playPauseIcon = togglePlayButton.querySelector('i');
  
    let isDragging = false;
    // let currentPercentage = 25; // Default slider position
    let currentPercentage = parseInt(divider.getAttribute("start_pos")); // Default slider position
    
    divider.style.left = `${currentPercentage}%`;
    divider.style.visibility = 'visible';
    // divider.style.animation = 'wiggle 1s ease-in-out';
    afterVideo.style.clipPath = `inset(0 ${100 - currentPercentage}% 0 0)`;

    beforeVideo.preload = 'auto';
    afterVideo.preload = 'auto';

      // Synchronize videos based on slider position
    const syncVideos = () => {
       if (Math.abs(beforeVideo.currentTime - afterVideo.currentTime) > 0.01) {
        afterVideo.currentTime = beforeVideo.currentTime;
      };
    };

    const togglePlayPause = () => {
    if (beforeVideo.paused) {
        beforeVideo.play();
        afterVideo.play();
        playPauseIcon.classList.remove('fa-play');
        playPauseIcon.classList.add('fa-pause');
    } else {
        beforeVideo.pause();
        afterVideo.pause();
        playPauseIcon.classList.remove('fa-pause');
        playPauseIcon.classList.add('fa-play');
    };
    syncVideos();
  }

    // Toggle play/pause functionality
    togglePlayButton.addEventListener('click', () => {
        togglePlayPause();
    });

    // Add click event listener to toggle play/pause for both videos
    beforeVideo.addEventListener('click', () => togglePlayPause(beforeVideo));
    afterVideo.addEventListener('click', () => togglePlayPause(afterVideo));

    // Seek slider functionality
    seekSlider.addEventListener('input', (e) => {
        const seekTime = (e.target.value / 100) * beforeVideo.duration;
        beforeVideo.currentTime = seekTime;
        afterVideo.currentTime = seekTime;
    });

    // Update seek slider as the video plays
    beforeVideo.addEventListener('timeupdate', () => {
        const progress = (beforeVideo.currentTime / beforeVideo.duration) * 100;
        seekSlider.value = progress;
        syncVideos();
    });

    divider.addEventListener('mousedown', () => {
      isDragging = true;
    });
  
    document.addEventListener('mouseup', () => {
      isDragging = false;
    });
  
    document.addEventListener('mousemove', (e) => {
      if (!isDragging) return;
  
      const rect = comparisonContainer.getBoundingClientRect();
      let offsetX = e.clientX - rect.left;
  
      // Ensure the divider stays within bounds
      offsetX = Math.max(0, Math.min(offsetX, rect.width));
  
      // Move the divider
      divider.style.left = `${offsetX}px`;
  
      // Adjust the "before" video's clip-path
      currentPercentage = (offsetX / rect.width) * 100;
      afterVideo.style.clipPath = `inset(0 ${100 - currentPercentage}% 0 0)`;

      if (currentPercentage != 0 && currentPercentage != 100) {
        syncVideos();
    };
    });
  });
});