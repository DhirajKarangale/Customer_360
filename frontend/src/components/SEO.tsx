import { Helmet } from 'react-helmet-async';

interface SEOProps {
  title?: string;
  description?: string;
  name?: string;
  type?: string;
  image?: string;
  url?: string;
  schema?: Record<string, any>;
}

export function SEO({ 
  title = "Customer 360 AI Insights Dashboard", 
  description = "AI-powered Customer 360 and Next Best Action platform for insurance agents. Combines customer profiles, policies, and interactions with RAG and LLMs to provide key insights and personalized recommendations.", 
  name = "Customer 360", 
  type = "website",
  image = "/icons/og-image.png",
  url = "https://customer-360.example.com/",
  schema
}: SEOProps) {
  
  const defaultSchema = {
    "@context": "https://schema.org",
    "@type": "WebSite",
    "name": name,
    "url": url,
    "description": description
  };

  const finalSchema = schema || defaultSchema;

  return (
    <Helmet>
      {/* Standard metadata tags */}
      <title>{title}</title>
      <meta name='description' content={description} />
      <link rel="canonical" href={url} />
      
      {/* Open Graph tags for Facebook, LinkedIn, etc. */}
      <meta property="og:type" content={type} />
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta property="og:image" content={image} />
      <meta property="og:url" content={url} />
      <meta property="og:site_name" content={name} />

      {/* Twitter tags */}
      <meta name="twitter:creator" content={name} />
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={title} />
      <meta name="twitter:description" content={description} />
      <meta name="twitter:image" content={image} />

      {/* JSON-LD Schema for SEO */}
      <script type="application/ld+json">
        {JSON.stringify(finalSchema)}
      </script>
    </Helmet>
  );
}
