import { PolicyLayout } from '../components/layout/PolicyLayout';

export default function PrivacyPage() {
  return (
    <PolicyLayout title="Privacy Policy">
          <p className="lead text-xl text-white/90 font-medium mb-8">
            At Customer 360 AI, we take your privacy seriously. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you visit our platform.
          </p>

          <h2 className="text-2xl mt-12 mb-4">1. Information We Collect</h2>
          <p>
            We may collect personal identification information from Users in a variety of ways, including, but not limited to, when Users visit our site, register on the site, place an order, fill out a form, and in connection with other activities, services, features or resources we make available on our Site.
          </p>

          <h2 className="text-2xl mt-12 mb-4">2. How We Use Information</h2>
          <p>
            We may use the information we collect from you to personalize your experience, improve our website, improve customer service, and process transactions.
          </p>

          <h2 className="text-2xl mt-12 mb-4">3. Data Security</h2>
          <p>
            We adopt appropriate data collection, storage and processing practices and security measures to protect against unauthorized access, alteration, disclosure or destruction of your personal information, username, password, transaction information and data stored on our Site.
          </p>
    </PolicyLayout>
  );
}
