// יצירת רכיב HTML פשוט יותר במקום להשתמש ב-LitElement
export class BrowzeePlanetAnimationElement extends HTMLElement {
  private animationFrameIds: number[] = [];
  private planetSystemElement: HTMLElement | null = null;
  private readonly colors = ['#f9a8d4', '#93c5fd', '#67e8f9', '#a78bfa'];
  
  static get is() {
    return 'browzee-planet-animation';
  }

  connectedCallback() {
    // יצירת Shadow DOM והוספת סגנונות והתוכן
    this.attachShadow({ mode: 'open' });
    if (this.shadowRoot) {
      // הוספת סגנונות
      const style = document.createElement('style');
      style.textContent = `
      :host {
          display: block;
          position: relative;
        width: 280px;
        height: 280px;
        margin: 0 auto 20px;
      }

      #planetSystem {
        position: relative;
          width: 100%;
        height: 100%;
      }

      #planet {
        position: absolute;
        top: 50%;
        left: 50%;
        width: 150px;
        height: 150px;
        margin-top: -75px;
        margin-left: -75px;
        background: radial-gradient(circle at 30% 30%, #a78bfa, #8b5cf6);
        border-radius: 50%;
        box-shadow: 0 0 40px rgba(139, 92, 246, 0.5);
        z-index: 10;
      }

      .orbit-wrapper {
        position: absolute;
        top: 50%;
        left: 50%;
        transform-origin: center;
        animation-name: rotate;
        animation-iteration-count: infinite;
        animation-timing-function: linear;
      }

      .star {
        position: absolute;
        border-radius: 50%;
        animation: shimmer 4s ease-in-out infinite;
        transition: z-index 0.3s, opacity 0.3s, filter 0.3s;
      }

      @keyframes shimmer {
        0%, 100% { opacity: 0.8; transform: scale(1); }
        50% { opacity: 1; transform: scale(1.1); }
      }

      @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
      }
    `;
      
      // יצירת מבנה ה-HTML הבסיסי
      const planetSystem = document.createElement('div');
      planetSystem.id = 'planetSystem';
      
      const planet = document.createElement('div');
      planet.id = 'planet';
      
      planetSystem.appendChild(planet);
      
      // הוספת הסגנונות והתוכן ל-Shadow DOM
      this.shadowRoot.appendChild(style);
      this.shadowRoot.appendChild(planetSystem);
      
      // שמירת הפנייה לאלמנט planetSystem
      this.planetSystemElement = planetSystem;
      
      // אתחול האנימציה
          this.initPlanetAnimation();
    }
  }

  disconnectedCallback() {
    // ניקוי מסגרות האנימציה כאשר האלמנט מוסר
    this.animationFrameIds.forEach(id => cancelAnimationFrame(id));
    this.animationFrameIds = [];
  }

  // העברת לוגיקת האנימציה למתודות של הרכיב
  private initPlanetAnimation() {
    if (!this.planetSystemElement) return;

    // ניקוי כוכבים קיימים (למעט div הכוכב)
    const stars = this.planetSystemElement.querySelectorAll('.orbit-wrapper');
    stars.forEach(star => star.remove());

    // ביטול מסגרות אנימציה קיימות
    this.animationFrameIds.forEach(id => cancelAnimationFrame(id));
    this.animationFrameIds = [];

    for (let i = 0; i < 25; i++) {
      const wrapper = document.createElement('div');
      wrapper.className = 'orbit-wrapper';

      const star = document.createElement('div');
      star.className = 'star';

      const size = 6 + Math.random() * 6;
      star.style.width = `${size}px`;
      star.style.height = `${size}px`;

      const color = this.colors[Math.floor(Math.random() * this.colors.length)];
      star.style.backgroundColor = color;
      star.style.boxShadow = `0 0 8px ${color}`;

      const radius = 80 + Math.random() * 60;
      const yOffset = -40 + Math.random() * 80;
      star.style.left = `${radius}px`;
      star.style.top = `${yOffset}px`;

      const duration = 20 + Math.random() * 30;
      const delay = Math.random() * duration;

      wrapper.style.animationDuration = `${duration}s`;
      wrapper.style.animationDelay = `-${delay}s`; // negative delay to offset starting point

      const startAngle = Math.random() * 360;
      wrapper.style.transform = `rotate(${startAngle}deg)`;

      this.startUpdateZIndex(star, duration, delay, startAngle);

      wrapper.appendChild(star);
      this.planetSystemElement.appendChild(wrapper);
    }
  }

  // פונקציה נפרדת להתחלת לולאת עדכון ה-z-index
  private startUpdateZIndex(star: HTMLElement, duration: number, delay: number, startAngle: number) {
    const updateZIndex = () => {
      // בדיקה אם האלמנט עדיין מחובר לפני שממשיכים
      if (!this.isConnected) {
        return;
      }

      const elapsed = (performance.now() / 1000 + delay) % duration;
      const angle = (elapsed / duration) * 360 + startAngle;
      const normalized = angle % 360;

      // הקצאת מחרוזות למאפייני סגנון
      if (normalized > 90 && normalized < 270) {
        star.style.zIndex = '1';
        star.style.opacity = '0.2';
        star.style.filter = "blur(1px)";
      } else {
        star.style.zIndex = '11'; // צריך להיות מעל #planet (z-index: 10)
        star.style.opacity = '1';
        star.style.filter = "none";
      }

      const id = requestAnimationFrame(updateZIndex);
      this.animationFrameIds.push(id);
    };

    const id = requestAnimationFrame(updateZIndex);
    this.animationFrameIds.push(id);
  }
}

// הגדרת הרכיב המותאם
customElements.define(BrowzeePlanetAnimationElement.is, BrowzeePlanetAnimationElement);

// הגדרת ממשק גלובלי למערכת בדיקת הטיפוסים של TypeScript
declare global {
  interface HTMLElementTagNameMap {
    'browzee-planet-animation': BrowzeePlanetAnimationElement;
  }
} 