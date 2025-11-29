# Responsive Design Guide

**Last Updated**: 2025-11-15
**Project**: Recipe Management System Frontend

---

## Overview

This document describes the responsive design implementation for the Recipe Management System. The application is fully responsive and optimized for all screen sizes from 320px (iPhone 5/SE) to large desktop displays (1920px+).

## Breakpoints

We use a mobile-first approach with the following breakpoints:

| Device Type | Breakpoint | Width Range | Usage |
|-------------|-----------|-------------|--------|
| Mobile | `max-width: 767px` | 320px - 767px | Small phones to large phones |
| Tablet | `min-width: 768px` and `max-width: 1023px` | 768px - 1023px | iPads and tablets |
| Desktop | `min-width: 1024px` | 1024px - 1279px | Laptops and small desktops |
| Large Desktop | `min-width: 1280px` | 1280px+ | Large monitors |

## Responsive Utilities

### Custom Hooks

#### `useMediaQuery(query: string)`

Detects if a media query matches and updates reactively.

```typescript
import { useMediaQuery } from '@/hooks/useMediaQuery';

const isLandscape = useMediaQuery('(orientation: landscape)');
const isPrint = useMediaQuery('print');
```

#### `useBreakpoints()`

Provides predefined breakpoint detection.

```typescript
import { useBreakpoints } from '@/hooks/useMediaQuery';

const {
  isMobile,        // true if width <= 767px
  isTablet,        // true if 768px <= width <= 1023px
  isDesktop,       // true if width >= 1024px
  isLargeDesktop,  // true if width >= 1280px
  isMobileOrTablet, // convenience flag
  isTabletOrDesktop // convenience flag
} = useBreakpoints();
```

#### `useIsTouchDevice()`

Detects if the device supports touch input.

```typescript
import { useIsTouchDevice } from '@/hooks/useMediaQuery';

const isTouchDevice = useIsTouchDevice();
```

#### `useSwipe(handlers, config)`

Detects touch swipe gestures.

```typescript
import { useSwipe } from '@/hooks/useSwipe';

const { ref, isSwiping, swipeDirection } = useSwipe({
  onSwipeLeft: () => console.log('Swiped left'),
  onSwipeRight: () => console.log('Swiped right'),
  onSwipeUp: () => console.log('Swiped up'),
  onSwipeDown: () => console.log('Swiped down'),
}, {
  minSwipeDistance: 50,  // minimum pixels to trigger
  maxSwipeTime: 500,     // maximum milliseconds
  preventDefaultTouchMove: false,
});

return <div ref={ref}>Swipeable content</div>;
```

## Component-Specific Responsive Behavior

### Navigation

**Desktop (>= 768px)**:
- Horizontal navigation bar
- Text links visible in header
- Add Recipe button with icon and text

**Mobile (< 768px)**:
- Hamburger menu button in top-right
- Collapsible dropdown menu
- Full-width menu items with touch-friendly spacing
- Add Recipe button in menu

```typescript
// components/layout/Navigation.tsx
const { isMobile } = useBreakpoints();

return (
  <header>
    {/* Desktop navigation */}
    <nav className="hidden md:flex">...</nav>

    {/* Mobile hamburger button */}
    <button className="md:hidden">...</button>

    {/* Mobile dropdown menu */}
    {isMobileMenuOpen && (
      <div className="md:hidden">...</div>
    )}
  </header>
);
```

### Filter Panel

**Desktop (>= 1024px)**:
- Sticky sidebar (width: 256px)
- Always visible
- Positioned on left side of content

**Mobile (< 1024px)**:
- Filter button in header
- Full-screen drawer overlay
- Slides in from left with backdrop
- Close button in top-right

```typescript
// HomePage.tsx
<aside className="hidden lg:block w-64">
  <FilterPanel />
</aside>

<button className="lg:hidden" onClick={openFilters}>
  Filters
</button>

{isMobileFiltersOpen && (
  <div className="fixed inset-0 z-50 lg:hidden">
    <div className="backdrop" />
    <div className="drawer">
      <FilterPanel />
    </div>
  </div>
)}
```

### Recipe Carousel

**Desktop (>= 768px)**:
- Arrow buttons visible
- Keyboard navigation (arrow keys)
- Mouse scroll support

**Mobile (< 768px)**:
- Touch swipe gestures
- Arrow buttons hidden
- Native touch scroll

```typescript
// components/RecipeCarousel.tsx
const { isMobile } = useBreakpoints();
const { ref } = useSwipe({
  onSwipeLeft: () => scrollRight(),
  onSwipeRight: () => scrollLeft(),
});

return (
  <div>
    {/* Arrows hidden on mobile */}
    {!isMobile && showLeftArrow && <button>←</button>}

    <div ref={ref} className="overflow-x-auto">
      {/* Cards */}
    </div>

    {!isMobile && showRightArrow && <button>→</button>}
  </div>
);
```

### Forms

**All Inputs**:
- Minimum height: 44px (touch-friendly)
- Font size: 16px (prevents iOS zoom)
- Full-width on mobile
- Proper spacing between fields

```css
/* index.css */
@media (max-width: 767px) {
  input:not([type="checkbox"]):not([type="radio"]),
  select,
  textarea {
    min-height: 44px;
    font-size: 16px; /* Prevents iOS zoom */
  }
}
```

### Modals

**Desktop**:
- Centered with max-width
- Max height: 90vh with scroll

**Mobile**:
- Nearly full-screen
- Small padding for backdrop
- Bottom-up animation option

```typescript
<div className="fixed inset-0 z-50">
  <div className="bg-black bg-opacity-50" onClick={close} />
  <div className="bg-white w-full max-w-2xl max-h-[90vh] overflow-y-auto">
    {/* Modal content */}
  </div>
</div>
```

## CSS Utilities

### Preventing Horizontal Scroll

```css
/* index.css */
html,
body {
  overflow-x: hidden;
  max-width: 100vw;
}

.container {
  max-width: 100%;
}
```

### Touch-Friendly Targets

```css
/* Minimum 44px touch targets on mobile */
@media (max-width: 767px) {
  button,
  a[role="button"],
  input[type="button"],
  input[type="submit"] {
    min-height: 44px;
    min-width: 44px;
  }
}
```

### Smooth Scrolling

```css
html {
  scroll-behavior: smooth;
}
```

### Swipeable Elements

```css
.swipeable {
  -webkit-user-select: none;
  user-select: none;
  -webkit-touch-callout: none;
}
```

## Tailwind Responsive Classes

Use Tailwind's responsive modifiers for styling:

```jsx
<div className="
  w-full           // mobile: full width
  md:w-1/2         // tablet: half width
  lg:w-1/3         // desktop: one-third
  xl:w-1/4         // large: one-quarter
">
  Content
</div>

<nav className="
  hidden           // mobile: hidden
  md:flex          // tablet+: flex
  md:items-center
  md:space-x-8
">
  Desktop Nav
</nav>

<button className="
  md:hidden        // desktop: hidden
">
  Mobile Menu
</button>
```

## Testing Responsive Design

### Unit Tests

Test responsive hooks:

```typescript
import { renderHook } from '@testing-library/react';
import { useBreakpoints } from '@/hooks/useMediaQuery';

it('should detect mobile viewport', () => {
  window.matchMedia = jest.fn().mockImplementation(query => ({
    matches: query === '(max-width: 767px)',
    // ... other properties
  }));

  const { result } = renderHook(() => useBreakpoints());
  expect(result.current.isMobile).toBe(true);
});
```

### E2E Tests (Puppeteer)

Test on multiple viewports:

```typescript
import puppeteer from 'puppeteer';

it('should not have horizontal scroll on mobile', async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  // iPhone SE viewport
  await page.setViewport({ width: 375, height: 667 });
  await page.goto('http://localhost:3000');

  const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
  const viewportWidth = await page.evaluate(() => window.innerWidth);

  expect(bodyWidth).toBeLessThanOrEqual(viewportWidth);

  await browser.close();
});
```

### Manual Testing Checklist

Test on these viewports:

- [ ] 320x568 (iPhone 5/SE) - Smallest supported
- [ ] 375x667 (iPhone SE/6/7/8) - Common small phone
- [ ] 414x896 (iPhone 11/XR) - Large phone
- [ ] 768x1024 (iPad Portrait) - Tablet
- [ ] 1024x768 (iPad Landscape) - Tablet
- [ ] 1280x720 (Laptop) - Small desktop
- [ ] 1920x1080 (Desktop) - Large desktop

### Responsive Testing Tools

**Browser DevTools**:
1. Open DevTools (F12)
2. Click Device Toolbar icon (Ctrl+Shift+M)
3. Select device or set custom dimensions
4. Test touch events with device mode

**Online Tools**:
- Responsively App (desktop app for multiple viewports)
- BrowserStack (real device testing)
- Chrome DevTools Device Mode

## Common Responsive Patterns

### Show/Hide Based on Breakpoint

```jsx
import { useBreakpoints } from '@/hooks/useMediaQuery';

const { isMobile } = useBreakpoints();

return (
  <>
    {isMobile ? (
      <MobileComponent />
    ) : (
      <DesktopComponent />
    )}
  </>
);
```

### Conditional Props

```jsx
const { isMobile } = useBreakpoints();

return (
  <RecipeGrid
    columns={isMobile ? 1 : isTablet ? 2 : 3}
    spacing={isMobile ? 'compact' : 'normal'}
  />
);
```

### Dynamic Class Names

```jsx
const { isMobile, isDesktop } = useBreakpoints();

return (
  <div className={`
    ${isMobile ? 'px-4' : 'px-8'}
    ${isDesktop ? 'max-w-7xl' : 'max-w-3xl'}
  `}>
    Content
  </div>
);
```

## Performance Considerations

### Lazy Loading by Screen Size

```typescript
import { lazy, Suspense } from 'react';
import { useBreakpoints } from '@/hooks/useMediaQuery';

const DesktopSidebar = lazy(() => import('./DesktopSidebar'));

const { isDesktop } = useBreakpoints();

return isDesktop ? (
  <Suspense fallback={<SidebarSkeleton />}>
    <DesktopSidebar />
  </Suspense>
) : null;
```

### Efficient Media Queries

The `useMediaQuery` hook uses efficient event listeners:
- Single listener per query
- Automatic cleanup on unmount
- No polling or intervals

### Touch Event Performance

Touch gesture detection uses passive event listeners:
```typescript
element.addEventListener('touchstart', handler, { passive: true });
```

## Accessibility

### Touch Targets

All interactive elements meet WCAG 2.1 Level AA requirements:
- Minimum 44x44 pixels for touch targets
- Adequate spacing between elements (8px minimum)

### Keyboard Navigation

Desktop users can navigate without touch:
- All interactive elements are keyboard-accessible
- Focus indicators visible
- Tab order logical

### Focus Management

When switching between mobile/desktop:
- Focus is maintained where possible
- No focus traps in modals
- Escape key closes overlays

## Troubleshooting

### Horizontal Scroll on Mobile

**Problem**: Page scrolls horizontally on mobile

**Solutions**:
1. Check for fixed-width elements
2. Verify no negative margins
3. Use `max-width: 100%` on images
4. Check DevTools for overflow

```javascript
// Debug overflow
document.querySelectorAll('*').forEach(el => {
  if (el.scrollWidth > window.innerWidth) {
    console.log('Overflow:', el);
  }
});
```

### Touch Gestures Not Working

**Problem**: Swipe gestures don't trigger

**Solutions**:
1. Ensure element has `touchstart` listener
2. Check `minSwipeDistance` isn't too high
3. Verify `maxSwipeTime` is reasonable
4. Check for conflicting touch handlers

### Font Zoom on iOS

**Problem**: iOS zooms in when focusing inputs

**Solutions**:
1. Set minimum font-size to 16px
2. Use `user-scalable=no` (not recommended)
3. Add viewport meta tag properly

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Layout Shift on Breakpoint

**Problem**: Content jumps when crossing breakpoint

**Solutions**:
1. Use `min-height` to reserve space
2. Avoid changing dimensions abruptly
3. Use CSS transitions for smooth changes
4. Test with Chrome DevTools rendering panel

## Best Practices

1. **Mobile First**: Write base styles for mobile, override for larger screens
2. **Touch Targets**: Minimum 44x44 pixels for all interactive elements
3. **Font Sizes**: Minimum 16px for inputs to prevent iOS zoom
4. **Breakpoints**: Use consistent breakpoints across the app
5. **Testing**: Test on real devices when possible
6. **Performance**: Use passive event listeners for touch events
7. **Images**: Use responsive images with srcset
8. **Container Widths**: Use max-width, not fixed width
9. **Spacing**: Reduce padding/margins on mobile
10. **Navigation**: Simplify navigation on small screens

## Further Reading

- [MDN: Responsive Design](https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Responsive_Design)
- [Web.dev: Responsive Web Design Basics](https://web.dev/responsive-web-design-basics/)
- [WCAG 2.1: Touch Target Size](https://www.w3.org/WAI/WCAG21/Understanding/target-size.html)
- [React Hooks: Window Dimensions](https://usehooks.com/useWindowSize/)
