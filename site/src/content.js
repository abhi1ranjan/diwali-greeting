/*
 * ─────────────────────────────────────────────────────────────────────────────
 *  EDIT THIS FILE to personalise the greeting. It is the only file you need.
 * ─────────────────────────────────────────────────────────────────────────────
 *  - Plain text only. Markup is never interpreted (everything is set with
 *    textContent), so "<b>" will appear literally.
 *  - If you change the headline, message, Hindi line, sign-off or blessing,
 *    also update the matching text inside <main> in site/index.html. That copy
 *    is what visitors see when JavaScript is unavailable, and what link
 *    previews read.
 *  - Never put private information here: this file is public on GitHub Pages.
 */
window.DIWALI_CONTENT = Object.freeze({
  sender: 'Abhishek',

  recipient: {
    // Salutation reads: "<greetingWord> <name from ?to=, or fallback>,"
    greetingWord: 'Dear',
    fallback: 'friends and family',
    // Optional URL personalisation, e.g. .../diwali-greeting/?to=Ananya
    // Set features.urlPersonalization to false to ignore the parameter.
    param: 'to'
  },

  eyebrow: 'A light from my home to yours',

  threshold: {
    line: 'A little light is waiting for you.',
    button: 'Light the diya'
  },

  headline: 'Happy Diwali',

  // Approved line only. Do not replace with machine translation.
  hindiLine: 'दीपावली की हार्दिक शुभकामनाएँ',

  message:
    'May every light you kindle bring warmth to your home, courage to your heart, ' +
    'and joy to the paths we share. Wishing you and your loved ones a Diwali filled ' +
    'with peace, laughter, good health, and bright new beginnings.',

  signoff: 'With warmth,',

  blessing:
    'From my home to yours, may the light stay with you long after the lamps grow quiet.',

  momentsTitle: 'Little moments that light up the year',

  /*
   * Memory moments (3 to 5 shown). See ASSETS.md for photo preparation.
   *  src:         'assets/photos/<file>.webp' (leave '' to show a placeholder)
   *  orientation: 'portrait' (4:5, ~1200x1500) or 'landscape' (3:2, ~1600x1067)
   *  width/height: the real pixel size of the file (prevents layout shift)
   *  alt:         describe what is in the photo for someone who cannot see it
   *  caption, when, where: short, optional
   */
  moments: [
    {
      src: 'assets/photos/moment-1.webp',
      orientation: 'portrait',
      width: 960,
      height: 1200,
      alt: 'A smiling cricketer sits cross-legged on the grass at night, holding up a ball beside a tall gold trophy marked "ICL 2026 Winners".',
      caption: '',
      when: '',
      where: ''
    },
    {
      src: 'assets/photos/moment-2.webp',
      orientation: 'portrait',
      width: 960,
      height: 1200,
      alt: 'Two friends pose on a floodlit cricket ground; one in a navy team jersey and medal holds a bat, the other wears a white "Heartland Heroes" jersey.',
      caption: '',
      when: '',
      where: ''
    },
    {
      src: 'assets/photos/moment-3.webp',
      orientation: 'landscape',
      width: 1280,
      height: 853,
      alt: 'A cricketer sitting on the grass throws his arms wide in celebration, a ball in one hand and the winners trophy in the other.',
      caption: '',
      when: '',
      where: ''
    },
    {
      src: 'assets/photos/moment-4.webp',
      orientation: 'portrait',
      width: 720,
      height: 900,
      alt: 'The top of a carved stone temple tower at night, its row of golden kalashas glowing against a dark sky.',
      caption: '',
      when: '',
      where: ''
    },
    {
      src: 'assets/photos/moment-5.webp',
      orientation: 'landscape',
      width: 1600,
      height: 1067,
      alt: 'The sun sets behind a cloud over a green sports ground, sending rays of light across the sky above the trees.',
      caption: '',
      when: '',
      where: ''
    }
  ],

  share: {
    title: 'Happy Diwali',
    text: 'A little light is waiting for you.'
  },

  sound: {
    // '' = an original raga-style loop synthesised in the browser (no file needed).
    // Or a local file you own or have licensed, such as
    // 'assets/audio/diwali-loop.m4a' (see ASSETS.md).
    src: '',
    loop: true,
    // true: music starts when the visitor clicks "Light the diya".
    // false: music stays off until the visitor turns on the Music button.
    startOnLight: true,
    // 0.05 to 0.6. Music always fades in to this level.
    volume: 0.35
  },

  features: {
    // Set to false to hide the memory section until you add real photos.
    moments: true,
    // Looping music with a Music on/off button. Nothing plays before the first click.
    sound: true,
    // Share button (Web Share API) with a copy-link fallback.
    share: true,
    hindiLine: true,
    urlPersonalization: true,
    // 'full' | 'gentle' | 'minimal'. Visitors who prefer reduced motion
    // always get the minimal, static version.
    animation: 'full'
  }
});
