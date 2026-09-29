import { Pool } from 'pg';

export const dynamic = 'force-dynamic';

interface Finding {
  id: number;
  severity: string;
  scanner: string;
  rule_id: string;
  title: string;
  file_path: string;
}

// Initialize standard Postgres connection pool
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

export default async function DashboardPage() {
  let findings: Finding[] = [];
  
  try {
    const { rows } = await pool.query(`
      SELECT * FROM findings 
      ORDER BY 
        CASE severity
          WHEN 'CRITICAL' THEN 1
          WHEN 'HIGH' THEN 2
          WHEN 'MEDIUM' THEN 3
          WHEN 'LOW' THEN 4
          ELSE 5
        END
    `);
    findings = rows;
  } catch (error) {
    console.error("Database query error:", error);
  }

  return (
    <main className="p-8 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">🛡️ TrustLens Security Dashboard</h1>
      
      <div className="bg-white shadow-md rounded-lg overflow-hidden border border-gray-200">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-6 py-4 font-medium text-gray-900">Severity</th>
              <th className="px-6 py-4 font-medium text-gray-900">Scanner</th>
              <th className="px-6 py-4 font-medium text-gray-900">Issue</th>
              <th className="px-6 py-4 font-medium text-gray-900">File Path</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {findings.map((finding) => (
              <tr key={finding.id} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                    finding.severity === 'CRITICAL' ? 'bg-red-100 text-red-800' :
                    finding.severity === 'HIGH' ? 'bg-orange-100 text-orange-800' :
                    finding.severity === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-blue-100 text-blue-800'
                  }`}>
                    {finding.severity}
                  </span>
                </td>
                <td className="px-6 py-4 font-semibold text-gray-600">
                  {finding.scanner}
                </td>
                <td className="px-6 py-4">
                  <p className="font-medium text-gray-900">{finding.title}</p>
                  <p className="text-gray-500 text-xs mt-1">{finding.rule_id}</p>
                </td>
                <td className="px-6 py-4 text-gray-500 font-mono text-xs">
                  {finding.file_path}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {findings.length === 0 && (
          <div className="p-8 text-center text-gray-500">
            No vulnerabilities found or database is unreachable!
          </div>
        )}
      </div>
    </main>
  );
}