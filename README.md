# Intunnel Consulting - Static Website

A fast, accessible, one-page marketing website for Intunnel Consulting built with static HTML, CSS, and JavaScript. Designed to be hosted on GitHub Pages with no build process required.

## 🚀 Quick Start

1. **Clone or download** this repository
2. **Update configuration** in `config.json`
3. **Deploy to GitHub Pages** (instructions below)

## 📁 Project Structure

```
/
├── index.html              # Main HTML file
├── config.json            # Configuration settings
├── README.md              # This file
├── assets/
│   ├── css/
│   │   └── styles.css     # Custom styles and utilities
│   ├── js/
│   │   ├── app.js         # Main JavaScript functionality
│   │   └── data.js        # Case studies and services data
│   ├── img/
│   │   ├── logo.svg       # Logo placeholder
│   │   ├── og-image.svg   # Open Graph image
│   │   └── platforms/     # Platform badge icons
│   └── icons/             # Additional icons (if needed)
```

## ⚙️ Configuration

Update `config.json` with your form and calendar settings:

```json
{
  "formEndpoint": "https://formspree.io/f/YOUR_FORM_ID",
  "calendly": "https://calendly.com/your-link"
}
```

### Form Setup Options

**Option 1: Formspree (Recommended)**
1. Go to [formspree.io](https://formspree.io)
2. Create a new form
3. Copy the form endpoint URL
4. Update `config.json` with your endpoint

**Option 2: Web3Forms**
1. Go to [web3forms.com](https://web3forms.com)
2. Create a new form
3. Copy the form endpoint URL
4. Update `config.json` with your endpoint

## 🚀 Deployment to GitHub Pages

### Method 1: Using GitHub Web Interface

1. **Create a new repository** on GitHub named `intunnelconsulting.github.io`
2. **Upload all files** to the repository
3. **Enable GitHub Pages**:
   - Go to repository Settings
   - Scroll to "Pages" section
   - Set Source to "Deploy from a branch"
   - Select "main" branch and "/ (root)" folder
   - Click "Save"
4. **Access your site** at `https://intunnelconsulting.github.io/`

### Method 2: Using Git Command Line

```bash
# Clone the repository
git clone https://github.com/yourusername/intunnelconsulting.github.io.git
cd intunnelconsulting.github.io

# Copy all files to the repository folder
# (copy index.html, config.json, assets/, etc.)

# Commit and push
git add .
git commit -m "Initial commit"
git push origin main

# Enable GitHub Pages in repository settings
# Go to Settings > Pages > Source > Deploy from branch > main > Save
```

## 🎨 Customization

### Updating Content

**Case Studies**: Edit `assets/js/data.js` to update case studies and services
**Styling**: Modify `assets/css/styles.css` for custom styles
**Brand Colors**: Update CSS variables in `styles.css`:
```css
:root {
  --primary: #2340FF;        /* Your primary color */
  --primary-dark: #1A30CC;   /* Darker shade for hover */
  --ink: #0B1020;            /* Text color */
}
```

### Adding Images

1. **Optimize images** before adding (use tools like TinyPNG)
2. **Place in** `assets/img/` directory
3. **Update HTML** to reference new images
4. **Use WebP/AVIF** format for better performance

## 📊 Performance Features

- **Lighthouse Score**: Optimized for 95+ Performance, 100 Accessibility, 100 SEO
- **Lazy Loading**: Images load only when needed
- **Smooth Scrolling**: Enhanced with Lenis library
- **Animations**: GSAP-powered with reduced motion support
- **CDN Assets**: Tailwind CSS, GSAP, and Lenis loaded from CDNs

## 🔧 Technical Stack

- **HTML5**: Semantic markup with proper accessibility
- **Tailwind CSS**: Utility-first CSS framework via CDN
- **Vanilla JavaScript**: ES6 modules with modern features
- **GSAP**: Professional animations and scroll triggers
- **Lenis**: Smooth scrolling library
- **Formspree/Web3Forms**: Form handling without server

## 📱 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 🛠️ Development

### Local Development

1. **Open** `index.html` in a web browser
2. **Use a local server** for testing forms:
   ```bash
   # Python 3
   python -m http.server 8000
   
   # Node.js
   npx serve .
   ```

### Testing

- **Lighthouse**: Run performance audits
- **Accessibility**: Test with screen readers
- **Forms**: Verify form submission works
- **Mobile**: Test responsive design

## 📈 SEO Features

- **Meta Tags**: Open Graph and Twitter Cards
- **JSON-LD**: Structured data for search engines
- **Semantic HTML**: Proper heading hierarchy
- **Fast Loading**: Optimized for Core Web Vitals

## 🔒 Security

- **HTTPS**: Required for GitHub Pages
- **Form Protection**: Honeypot fields for spam prevention
- **No Server**: Static site reduces attack surface

## 📞 Support

For questions or issues:
1. Check the configuration in `config.json`
2. Verify form endpoints are working
3. Test locally before deploying
4. Check browser console for errors

## 📄 License

This project is open source and available under the MIT License.

---

**Built with ❤️ for Intunnel Consulting**
