import { PolicyLayout } from '../components/layout/PolicyLayout';

export default function TermsPage() {
  return (
    <PolicyLayout title="Terms of Service">
          <p className="lead text-xl text-white/90 font-medium mb-8">
            These Terms of Service ("Terms") govern your access to and use of the Customer 360 AI platform. Please read these Terms carefully before using our services.
          </p>

          <h2 className="text-2xl mt-12 mb-4">1. Acceptance of Terms</h2>
          <p>
            By accessing or using our services, you agree to be bound by these Terms and our Privacy Policy. If you do not agree to these Terms, you may not access or use the services.
          </p>

          <h2 className="text-2xl mt-12 mb-4">2. User Responsibilities</h2>
          <p>
            You are responsible for safeguarding the password that you use to access the services and for any activities or actions under your password. You agree not to disclose your password to any third party.
          </p>

          <h2 className="text-2xl mt-12 mb-4">3. Limitation of Liability</h2>
          <p>
            In no event shall Customer 360 AI, nor its directors, employees, partners, agents, suppliers, or affiliates, be liable for any indirect, incidental, special, consequential or punitive damages, including without limitation, loss of profits, data, use, goodwill, or other intangible losses, resulting from your access to or use of or inability to access or use the services.
          </p>
    </PolicyLayout>
  );
}
