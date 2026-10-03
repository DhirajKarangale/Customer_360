import { Mail, Phone, Code, Rocket, Sparkles } from 'lucide-react';
import { useUIStore } from '../store/useUIStore';

const teamMembers = [
  {
    name: "Dhiraj Karangale",
    role: "Full Stack Developer",
    phone: "+91 7620320595",
    email: "dakarangale02@gmail.com",
    avatar: "./dhiraj_1.png"
  },
  {
    name: "Vedang Joshi",
    role: "Full Stack Developer",
    phone: "+91 8668604093",
    email: "vedangjoshi772@gmail.com",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Vedang&backgroundColor=ffdfbf,c0aede"
  },
  {
    name: "Sravan Kumar",
    role: "Full Stack Developer",
    phone: "+91 9739369262",
    email: "gogisettysravankumar@gmail.com",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Sravan&backgroundColor=b6e3f4,ffdfbf"
  },
  {
    name: "Harshul Nanwani",
    role: "Full Stack Developer",
    phone: "+91 9755255511",
    email: "harshul26@gmail.com",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Harshul&backgroundColor=ffdfbf,d1d4f9"
  }
];

export default function AboutPage() {
  const showToast = useUIStore((state) => state.showToast);

  const handleCopy = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    showToast(`${label} copied to clipboard!`, 'text-emerald-400', 3000);
  };

  return (
    <div className="relative min-h-[80vh] w-full overflow-hidden rounded-2xl bg-[#030712] animate-in fade-in zoom-in-95 duration-500 p-8 shadow-2xl border border-white/5">

      {/* Background ambient glows */}
      <div className="absolute top-0 left-1/4 h-[500px] w-[500px] rounded-full bg-indigo-600/20 blur-[120px] pointer-events-none mix-blend-screen" />
      <div className="absolute bottom-0 right-1/4 h-[400px] w-[400px] rounded-full bg-violet-600/20 blur-[100px] pointer-events-none mix-blend-screen" />

      <div className="relative z-10 mx-auto max-w-6xl">

        {/* Header Section */}
        <div className="flex flex-col items-center justify-center text-center space-y-6 mb-16 mt-8">
          <div className="relative group">
            <div className="absolute -inset-1 rounded-full bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 opacity-75 blur transition duration-500 group-hover:opacity-100 group-hover:duration-200"></div>
            <div className="relative flex h-32 w-32 items-center justify-center overflow-hidden rounded-full bg-black border border-white/10 p-4">
              {/* Fallback text if logo fails to load, but typically it will show the logo */}
              <img
                src="/DCoders.webp"
                alt="DCoders Logo"
                className="h-full w-full object-contain transform transition-transform duration-500 group-hover:scale-110"
                onError={(e) => {
                  (e.target as HTMLImageElement).src = 'https://api.dicebear.com/7.x/initials/svg?seed=DC&backgroundColor=000000';
                }}
              />
            </div>
          </div>

          <div className="space-y-4">
            <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-indigo-300 via-white to-purple-300 drop-shadow-sm">
              Team DCoders
            </h1>
            <p className="flex items-center justify-center gap-2 text-lg text-indigo-200/80 max-w-2xl mx-auto font-medium">
              <Rocket className="h-5 w-5 text-indigo-400" />
              Building the future at the Snowflake Hackathon
              <Sparkles className="h-5 w-5 text-purple-400" />
            </p>
          </div>
        </div>

        {/* Team Members Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {teamMembers.map((member, index) => (
            <div
              key={index}
              className="group relative flex flex-col rounded-2xl bg-white/5 border border-white/10 p-6 backdrop-blur-md transition-all duration-300 hover:-translate-y-2 hover:bg-white/[0.08] hover:shadow-[0_8px_30px_rgb(0,0,0,0.12)] hover:border-white/20"
            >
              <div className="absolute inset-0 rounded-2xl bg-gradient-to-b from-indigo-500/0 via-transparent to-purple-500/5 opacity-0 transition-opacity duration-300 group-hover:opacity-100 pointer-events-none" />

              <div className="relative mb-6 flex justify-center">
                <div className="relative h-24 w-24 overflow-hidden rounded-full border-2 border-indigo-500/30 bg-black/50 p-1 transition-transform duration-300 group-hover:scale-110 group-hover:border-indigo-400">
                  <img
                    src={member.avatar}
                    alt={member.name}
                    className="h-full w-full rounded-full object-cover"
                  />
                </div>
              </div>

              <div className="flex flex-col items-center text-center flex-1">
                <h3 className="text-xl font-bold text-gray-100 tracking-wide mb-1 group-hover:text-white transition-colors">
                  {member.name}
                </h3>
                <div className="flex items-center gap-1.5 text-sm font-medium text-indigo-300/80 mb-6 bg-indigo-500/10 px-3 py-1 rounded-full">
                  <Code className="h-3.5 w-3.5" />
                  {member.role}
                </div>

                <div className="mt-auto w-full space-y-3">
                  <button
                    type="button"
                    onClick={() => handleCopy(member.phone, 'Phone number')}
                    className="w-full cursor-pointer flex items-center gap-3 rounded-xl bg-black/40 p-3 text-sm text-gray-300 transition-colors hover:bg-black/60 hover:text-white border border-white/5 text-left"
                  >
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-500/20 text-indigo-400">
                      <Phone className="h-4 w-4" />
                    </div>
                    <span className="font-mono text-xs md:text-sm">{member.phone}</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => handleCopy(member.email, 'Email address')}
                    className="w-full cursor-pointer flex items-center gap-3 rounded-xl bg-black/40 p-3 text-sm text-gray-300 transition-colors hover:bg-black/60 hover:text-white border border-white/5 overflow-hidden text-left"
                    title={member.email}
                  >
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-purple-500/20 text-purple-400">
                      <Mail className="h-4 w-4" />
                    </div>
                    <span className="truncate text-xs font-medium">{member.email}</span>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

      </div>
    </div>
  );
}
