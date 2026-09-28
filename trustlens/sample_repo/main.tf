# Intentionally vulnerable Terraform configuration for testing

# ============================================
# VULNERABILITY 1: Public S3 bucket without access control
# ============================================
resource "aws_s3_bucket" "bad_bucket" {
  bucket = "publicly-accessible-bucket"
  acl    = "public-read"  # HIGH RISK: Public access

  # VULNERABILITY 2: No encryption enabled
  # (encryption block is deliberately missing)

  # VULNERABILITY 3: No logging enabled
  # (server_side_encryption_configuration and logging blocks are missing)

  tags = {
    Name = "BadBucket"
  }
}

# VULNERABILITY: Public access policy
resource "aws_s3_bucket_public_access_block" "bad_bucket_access" {
  bucket = aws_s3_bucket.bad_bucket.id

  block_public_acls       = false  # Allow public ACLs
  block_public_policy     = false  # Allow public policy
  ignore_public_acls      = false  # Don't ignore public ACLs
  restrict_public_buckets = false  # Don't restrict public buckets
}

# ============================================
# VULNERABILITY 4: Security group open to the world
# ============================================
resource "aws_security_group" "bad_sg" {
  name        = "bad-security-group"
  description = "Security group with overly permissive rules"

  # VULNERABILITY: Ingress rule open to 0.0.0.0/0 (entire internet)
  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # CRITICAL: Open to entire internet
    description = "Allow all traffic from anywhere"
  }

  # VULNERABILITY: SSH open to world
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # HIGH: SSH exposed to internet
    description = "SSH access from anywhere"
  }

  # VULNERABILITY: No restricted egress
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "BadSecurityGroup"
  }
}

# ============================================
# VULNERABILITY 5: EC2 instance without encryption
# ============================================
resource "aws_instance" "bad_instance" {
  ami                    = "ami-0c55b159cbfafe1f0"
  instance_type          = "t2.micro"
  security_groups        = [aws_security_group.bad_sg.name]
  associate_public_ip_address = true  # VULNERABILITY: Public IP assignment

  # VULNERABILITY: No root block device encryption
  root_block_device {
    volume_type = "gp2"
    volume_size = 20
    # encrypted field is missing - volume is NOT encrypted
  }

  tags = {
    Name = "BadInstance"
  }
}

# ============================================
# VULNERABILITY 6: RDS database without encryption
# ============================================
resource "aws_db_instance" "bad_rds" {
  identifier     = "bad-database"
  engine         = "mysql"
  engine_version = "5.7"  # VULNERABILITY: Outdated version
  instance_class = "db.t2.micro"
  username       = "admin"
  password       = "badpassword123!"  # VULNERABILITY: Hard-coded password in code

  allocated_storage = 20
  storage_type      = "gp2"

  # VULNERABILITY: No encryption at rest
  storage_encrypted = false

  # VULNERABILITY: No backup
  backup_retention_period = 0

  # VULNERABILITY: Publicly accessible
  publicly_accessible = true

  skip_final_snapshot = true

  tags = {
    Name = "BadDatabase"
  }
}

# ============================================
# VULNERABILITY 7: KMS key without rotation
# ============================================
resource "aws_kms_key" "bad_key" {
  description             = "KMS key without rotation"
  deletion_window_in_days = 7
  enable_key_rotation     = false  # VULNERABILITY: Key rotation disabled

  tags = {
    Name = "BadKey"
  }
}

# ============================================
# VULNERABILITY 8: CloudTrail without validation
# ============================================
resource "aws_cloudtrail" "bad_trail" {
  name                          = "bad-trail"
  s3_bucket_name                = aws_s3_bucket.bad_bucket.id
  include_global_service_events = true
  is_multi_region_trail         = false  # VULNERABILITY: Not multi-region
  enable_log_file_validation    = false  # VULNERABILITY: No log validation
  depends_on                    = [aws_s3_bucket_policy.bad_trail_policy]
}

resource "aws_s3_bucket_policy" "bad_trail_policy" {
  bucket = aws_s3_bucket.bad_bucket.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.bad_bucket.arn}/*"
      }
    ]
  })
}
