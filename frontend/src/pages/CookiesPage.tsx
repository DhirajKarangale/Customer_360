import { SEO } from '../components/SEO';
import { PolicyLayout } from '../components/layout/PolicyLayout';

export default function CookiesPage() {
  return (
    <>
      <SEO title="Cookies | Customer 360 AI Insights" />
      <OriginalCookiesPage />
    </>
  );
}

function OriginalCookiesPage() {
  return (
    <PolicyLayout title="Cookie Policy">
          <p className="lead text-xl text-white/90 font-medium mb-8">
            This Cookie Policy explains how Customer 360 AI uses cookies and similar technologies to recognize you when you visit our website. It explains what these technologies are and why we use them, as well as your rights to control our use of them.
          </p>

          <h2 className="text-2xl mt-12 mb-4">What are cookies?</h2>
          <p>
            Cookies are small data files that are placed on your computer or mobile device when you visit a website. Cookies are widely used by website owners in order to make their websites work, or to work more efficiently, as well as to provide reporting information.
          </p>

          <h2 className="text-2xl mt-12 mb-4">Why do we use cookies?</h2>
          <p>
            We use first-party and third-party cookies for several reasons. Some cookies are required for technical reasons in order for our website to operate, and we refer to these as "essential" or "strictly necessary" cookies. Other cookies also enable us to track and target the interests of our users to enhance the experience on our website.
          </p>

          <h2 className="text-2xl mt-12 mb-4">How can I control cookies?</h2>
          <p>
            You have the right to decide whether to accept or reject cookies. You can set or amend your web browser controls to accept or refuse cookies. If you choose to reject cookies, you may still use our website though your access to some functionality and areas of our website may be restricted.
          </p>
    </PolicyLayout>
  );
}
