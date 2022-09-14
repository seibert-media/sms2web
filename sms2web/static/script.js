if(document.readyState !== 'loading') {
  init()
} else {
  document.addEventListener('DOMContentLoaded', function () {
    init()
  })
}

function init() {
  console.log('init')
  update_times()
  if ((new URLSearchParams(window.location.search).get('page') || '0') === '0') {
    setInterval(update_list, 2000)
  }
  if ("Notification" in window) {
    set_notification_status()
    document.querySelector('.notify a').addEventListener('click', () => {
      Notification.requestPermission().then(set_notification_status)
    })
  }
}

function update_list() {
  var newest_sms = document.querySelector('.sms')
  if (newest_sms) {
    var timestamp = newest_sms.querySelector('[data-timestamp]').getAttribute('data-timestamp')
  } else {
    var timestamp = 0
  }
  fetch('/?since=' + timestamp + '&layout=false&page=0&per_page=999').then((response) => {
    return response.text()
  }).then((html) => {
    new DOMParser()
      .parseFromString(html, "text/html")
      .querySelectorAll('.sms')
      .forEach((sms) => {
        sms.setAttribute('data-highlight', 'True')
        document
          .querySelector('.sms_list')
          .insertBefore(sms, newest_sms)
        notifyMe(sms.querySelector('.message').innerText)
      })
    update_times()
  }).catch((err) => {
  	console.warn('ERROR:', err)
  })
}

function update_times() {
  document
    .querySelectorAll('[data-timestamp]')
    .forEach((element) => {
      element.innerHTML = timeSince(parseInt(element.getAttribute('data-timestamp')) * 1000)
    })
}

// https://stackoverflow.com/a/3177838/896424
function timeSince(date) {
  var seconds = Math.floor((new Date() - date) / 1000);
  var interval = seconds / 31536000;

  if (interval > 1) {
    return Math.floor(interval) + " years";
  }
  interval = seconds / 2592000;
  if (interval > 1) {
    return Math.floor(interval) + " months";
  }
  interval = seconds / 86400;
  if (interval > 1) {
    return Math.floor(interval) + " days";
  }
  interval = seconds / 3600;
  if (interval > 1) {
    return Math.floor(interval) + " hours";
  }
  interval = seconds / 60;
  if (interval > 1) {
    return Math.floor(interval) + " minutes";
  }
  return Math.floor(seconds) + " seconds";
}

// https://developer.mozilla.org/en-US/docs/Web/API/notification
function notifyMe(message) {
  if ("Notification" in window) {
    if (Notification.permission === "granted") {
      new Notification(message)
    }
  }
}

function set_notification_status() {
  document.querySelector('.notify').classList.remove("hidden")
  document.querySelector('.notify a').setAttribute('data-status', Notification.permission)
}
