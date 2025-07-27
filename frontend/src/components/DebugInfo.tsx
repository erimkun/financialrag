import React, { useEffect, useState } from 'react';

interface DebugInfoProps {
  className?: string;
}

export const DebugInfo: React.FC<DebugInfoProps> = ({ className }) => {
  const [cssLoaded, setCssLoaded] = useState(false);
  const [tailwindClasses, setTailwindClasses] = useState<string[]>([]);

  useEffect(() => {
    // CSS yüklenme kontrolü
    const testElement = document.createElement('div');
    testElement.className = 'bg-blue-500 text-white p-4 hidden';
    testElement.style.position = 'absolute';
    testElement.style.top = '-9999px';
    document.body.appendChild(testElement);

    const computedStyle = window.getComputedStyle(testElement);
    const hasBackground = computedStyle.backgroundColor === 'rgb(59, 130, 246)'; // bg-blue-500
    const hasPadding = computedStyle.padding === '16px'; // p-4
    const hasColor = computedStyle.color === 'rgb(255, 255, 255)'; // text-white

    setCssLoaded(hasBackground && hasPadding && hasColor);
    
    // Yüklenen CSS class'larını kontrol et
    const styleSheets = Array.from(document.styleSheets);
    const classes: string[] = [];
    
    try {
      styleSheets.forEach(sheet => {
        try {
          const rules = Array.from(sheet.cssRules || []);
          rules.forEach(rule => {
            if (rule instanceof CSSStyleRule && rule.selectorText) {
              if (rule.selectorText.includes('bg-') || 
                  rule.selectorText.includes('text-') ||
                  rule.selectorText.includes('flex') ||
                  rule.selectorText.includes('p-')) {
                classes.push(rule.selectorText);
              }
            }
          });
        } catch (e) {
          // CORS hatası - external stylesheet
        }
      });
    } catch (error) {
      console.log('CSS rules check error:', error);
    }

    setTailwindClasses(classes.slice(0, 10)); // İlk 10 class'ı göster
    
    document.body.removeChild(testElement);
  }, []);

  if (!className?.includes('debug-visible')) {
    return null;
  }

  return (
    <div className="fixed top-4 right-4 bg-slate-800 text-white p-4 rounded-lg shadow-lg z-50 max-w-sm text-xs">
      <h3 className="font-bold mb-2">🔍 Debug Info</h3>
      
      <div className="space-y-2">
        <div>
          <strong>Tailwind CSS:</strong> 
          <span className={cssLoaded ? 'text-green-400' : 'text-red-400'}>
            {cssLoaded ? ' ✅ Yüklendi' : ' ❌ Yüklenmedi'}
          </span>
        </div>
        
        <div>
          <strong>Test Element:</strong>
          <div className="bg-blue-500 text-white p-1 mt-1 rounded">
            Bu mavi ise CSS çalışıyor
          </div>
        </div>

        <div>
          <strong>Bulunan CSS Classes:</strong>
          <div className="max-h-20 overflow-y-auto mt-1">
            {tailwindClasses.length > 0 ? (
              tailwindClasses.map((cls, idx) => (
                <div key={idx} className="text-xs opacity-75">{cls}</div>
              ))
            ) : (
              <div className="text-red-400">Hiç class bulunamadı</div>
            )}
          </div>
        </div>

        <div>
          <strong>Viewport:</strong> {window.innerWidth}x{window.innerHeight}
        </div>
      </div>
    </div>
  );
};

export default DebugInfo;
