"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Icon } from "@iconify/react";
import { Button, Checkbox, Divider, Tooltip } from "@nextui-org/react";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { authenticate, createNewUser } from "@/actions/auth";
import { initiateSamlAuth } from "@/actions/integrations/saml";
import { PasswordRequirementsMessage } from "@/components/auth/oss/password-validator";
import { NotificationIcon, ProwlerExtended } from "@/components/icons";
import { ThemeSwitch } from "@/components/ThemeSwitch";
import { useToast } from "@/components/ui";
import { CustomButton, CustomInput } from "@/components/ui/custom";
import { CustomLink } from "@/components/ui/custom/custom-link";
import {
  Form,
  FormControl,
  FormField,
  FormMessage,
} from "@/components/ui/form";
import { ApiError, authFormSchema } from "@/types";

export const AuthForm = ({
  type,
  invitationToken,
  isCloudEnv,
  googleAuthUrl,
  githubAuthUrl,
  isGoogleOAuthEnabled,
  isGithubOAuthEnabled,
}: {
  type: string;
  invitationToken?: string | null;
  isCloudEnv?: boolean;
  googleAuthUrl?: string;
  githubAuthUrl?: string;
  isGoogleOAuthEnabled?: boolean;
  isGithubOAuthEnabled?: boolean;
}) => {
  const formSchema = authFormSchema(type);
  const router = useRouter();
  const searchParams = useSearchParams();
  const { toast } = useToast();

  useEffect(() => {
    const samlError = searchParams.get("sso_saml_failed");

    if (samlError) {
      // Add a delay to the toast to ensure it is rendered
      setTimeout(() => {
        toast({
          variant: "destructive",
          title: "SAML Authentication Error",
          description:
            "An error occurred while attempting to login via your Identity Provider (IdP). Please check your IdP configuration.",
        });
      }, 100);
    }
  }, [searchParams, toast]);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      email: "",
      password: "",
      isSamlMode: false,
      ...(type === "sign-up" && {
        name: "",
        company: "",
        confirmPassword: "",
        ...(invitationToken && { invitationToken }),
      }),
    },
  });

  const isLoading = form.formState.isSubmitting;
  const isSamlMode = form.watch("isSamlMode");

  const onSubmit = async (data: z.infer<typeof formSchema>) => {
    if (type === "sign-in") {
      if (data.isSamlMode) {
        const email = data.email.toLowerCase();
        if (isSamlMode) {
          form.setValue("password", "");
        }

        const result = await initiateSamlAuth(email);

        if (result.success && result.redirectUrl) {
          window.location.href = result.redirectUrl;
        } else {
          toast({
            variant: "destructive",
            title: "SAML Authentication Error",
            description:
              result.error || "An error occurred during SAML authentication.",
          });
        }
        return;
      }

      const result = await authenticate(null, {
        email: data.email.toLowerCase(),
        password: data.password,
      });
      if (result?.message === "Success") {
        router.push("/");
      } else if (result?.errors && "credentials" in result.errors) {
        form.setError("email", {
          type: "server",
          message: result.errors.credentials ?? "Incorrect email or password",
        });
      } else if (result?.message === "User email is not verified") {
        router.push("/email-verification");
      } else {
        toast({
          variant: "destructive",
          title: "Oops! Something went wrong",
          description: "An unexpected error occurred. Please try again.",
        });
      }
    }

    if (type === "sign-up") {
      const newUser = await createNewUser(data);

      if (!newUser.errors) {
        toast({
          title: "Success!",
          description: "The user was registered successfully.",
        });
        form.reset();

        if (isCloudEnv) {
          router.push("/email-verification");
        } else {
          router.push("/sign-in");
        }
      } else {
        newUser.errors.forEach((error: ApiError) => {
          const errorMessage = error.detail;
          switch (error.source.pointer) {
            case "/data/attributes/name":
              form.setError("name", { type: "server", message: errorMessage });
              break;
            case "/data/attributes/email":
              form.setError("email", { type: "server", message: errorMessage });
              break;
            case "/data/attributes/company_name":
              form.setError("company", {
                type: "server",
                message: errorMessage,
              });
              break;
            case "/data/attributes/password":
              form.setError("password", {
                type: "server",
                message: errorMessage,
              });
              break;
            case "/data":
              form.setError("invitationToken", {
                type: "server",
                message: errorMessage,
              });
              break;
            default:
              toast({
                variant: "destructive",
                title: "Oops! Something went wrong",
                description: errorMessage,
              });
          }
        });
      }
    }
  };

  return (
    <div className="relative flex h-screen w-screen">
      {/* Auth Form */}
      <div className="relative flex w-full items-center justify-center lg:w-full">
        {/* Background Pattern */}
        <div className="absolute h-full w-full bg-[radial-gradient(#6af400_1px,transparent_1px)] [background-size:16px_16px] [mask-image:radial-gradient(ellipse_50%_50%_at_50%_50%,#000_10%,transparent_80%)]"></div>

        <div className="relative z-10 flex w-full max-w-sm flex-col gap-4 rounded-large border-1 border-divider bg-white/90 px-8 py-10 shadow-small dark:bg-background/85 md:max-w-md">
          {/* Prowler Logo */}
          <div className="absolute -top-[100px] left-1/2 z-10 flex h-fit w-fit -translate-x-1/2">
            <ProwlerExtended width={300} />
          </div>
          <div className="flex items-center justify-between">
            <p className="pb-2 text-xl font-medium">
              {type === "sign-in"
                ? isSamlMode
                  ? "Sign in with SAML SSO"
                  : "Sign in"
                : "Sign up"}
            </p>
            <ThemeSwitch aria-label="Toggle theme" />
          </div>

          <Form {...form}>
            <form
              className="flex flex-col gap-4"
              onSubmit={form.handleSubmit(onSubmit)}
            >
              {type === "sign-up" && (
                <>
                  <CustomInput
                    control={form.control}
                    name="name"
                    type="text"
                    label="Name"
                    placeholder="Enter your name"
                    isInvalid={!!form.formState.errors.name}
                  />
                  <CustomInput
                    control={form.control}
                    name="company"
                    type="text"
                    label="Company name"
                    placeholder="Enter your company name"
                    isRequired={false}
                    isInvalid={!!form.formState.errors.company}
                  />
                </>
              )}
              <CustomInput
                control={form.control}
                name="email"
                type="email"
                label="Email"
                placeholder="Enter your email"
                isInvalid={!!form.formState.errors.email}
                showFormMessage={type !== "sign-in"}
              />
              {!isSamlMode && (
                <>
                  <CustomInput
                    control={form.control}
                    name="password"
                    password
                    isInvalid={
                      !!form.formState.errors.password ||
                      !!form.formState.errors.email
                    }
                  />
                  {type === "sign-up" && (
                    <PasswordRequirementsMessage
                      password={form.watch("password") || ""}
                    />
                  )}
                </>
              )}
              {/* {type === "sign-in" && (
                <div className="flex items-center justify-between px-1 py-2">
                  <Checkbox name="remember" size="sm">
                    Remember me
                  </Checkbox>
                  <Link className="text-default-500" href="#">
                    Forgot password?
                  </Link>
                </div>
              )} */}
              {type === "sign-up" && (
                <>
                  <CustomInput
                    control={form.control}
                    name="confirmPassword"
                    confirmPassword
                  />
                  {invitationToken && (
                    <CustomInput
                      control={form.control}
                      name="invitationToken"
                      type="text"
                      label="Invitation Token"
                      placeholder={invitationToken}
                      defaultValue={invitationToken}
                      isRequired={false}
                      isInvalid={!!form.formState.errors.invitationToken}
                      isDisabled={invitationToken !== null && true}
                    />
                  )}

                  {process.env.NEXT_PUBLIC_IS_CLOUD_ENV === "true" && (
                    <FormField
                      control={form.control}
                      name="termsAndConditions"
                      render={({ field }) => (
                        <>
                          <FormControl>
                            <Checkbox
                              isRequired
                              className="py-4"
                              size="sm"
                              checked={field.value}
                              onChange={(e) => field.onChange(e.target.checked)}
                            >
                              I agree with the&nbsp;
                              <CustomLink
                                href="https://prowler.com/terms-of-service/"
                                size="sm"
                              >
                                Terms of Service
                              </CustomLink>
                              &nbsp;of Prowler
                            </Checkbox>
                          </FormControl>
                          <FormMessage className="text-system-error dark:text-system-error" />
                        </>
                      )}
                    />
                  )}
                </>
              )}
              {type === "sign-in" && form.formState.errors?.email && (
                <div className="flex flex-row items-center text-system-error">
                  <NotificationIcon size={16} />
                  <p className="text-small">Invalid email or password</p>
                </div>
              )}
              <CustomButton
                type="submit"
                ariaLabel={type === "sign-in" ? "Log in" : "Sign up"}
                ariaDisabled={isLoading}
                className="w-full"
                variant="solid"
                color="action"
                size="md"
                radius="md"
                isLoading={isLoading}
                isDisabled={isLoading}
              >
                {isLoading ? (
                  <span>Loading</span>
                ) : (
                  <span>{type === "sign-in" ? "Log in" : "Sign up"}</span>
                )}
              </CustomButton>
            </form>
          </Form>

          {!invitationToken && type === "sign-in" && (
            <>
              <div className="flex items-center gap-4 py-2">
                <Divider className="flex-1" />
                <p className="shrink-0 text-tiny text-default-500">OR</p>
                <Divider className="flex-1" />
              </div>
              <div className="flex flex-col gap-2">
                {!isSamlMode && (
                  <>
                    <Tooltip
                      content={
                        <div className="flex-inline text-small">
                          Social Login with Google is not enabled.{" "}
                          <CustomLink href="https://docs.prowler.com/projects/prowler-open-source/en/latest/tutorials/prowler-app-social-login/#google-oauth-configuration">
                            Read the docs
                          </CustomLink>
                        </div>
                      }
                      placement="right-start"
                      shadow="sm"
                      isDisabled={isGoogleOAuthEnabled}
                      className="w-96"
                    >
                      <span>
                        <Button
                          startContent={
                            <Icon icon="flat-color-icons:google" width={24} />
                          }
                          variant="bordered"
                          className="w-full"
                          as="a"
                          href={googleAuthUrl}
                          isDisabled={!isGoogleOAuthEnabled}
                        >
                          Continue with Google
                        </Button>
                      </span>
                    </Tooltip>
                    <Tooltip
                      content={
                        <div className="flex-inline text-small">
                          Social Login with Github is not enabled.{" "}
                          <CustomLink href="https://docs.prowler.com/projects/prowler-open-source/en/latest/tutorials/prowler-app-social-login/#github-oauth-configuration">
                            Read the docs
                          </CustomLink>
                        </div>
                      }
                      placement="right-start"
                      shadow="sm"
                      isDisabled={isGithubOAuthEnabled}
                      className="w-96"
                    >
                      <span>
                        <Button
                          startContent={
                            <Icon
                              className="text-default-500"
                              icon="fe:github"
                              width={24}
                            />
                          }
                          variant="bordered"
                          className="w-full"
                          as="a"
                          href={githubAuthUrl}
                          isDisabled={!isGithubOAuthEnabled}
                        >
                          Continue with Github
                        </Button>
                      </span>
                    </Tooltip>
                  </>
                )}
                <Button
                  startContent={
                    !isSamlMode && (
                      <Icon
                        className="text-default-500"
                        icon="mdi:shield-key"
                        width={24}
                      />
                    )
                  }
                  variant="bordered"
                  className="w-full"
                  onClick={() => {
                    form.setValue("isSamlMode", !isSamlMode);
                  }}
                >
                  {isSamlMode ? "Back" : "Continue with SAML SSO"}
                </Button>
              </div>
            </>
          )}
          {type === "sign-in" ? (
            <p className="text-center text-small">
              Need to create an account?&nbsp;
              <CustomLink size="base" href="/sign-up" target="_self">
                Sign up
              </CustomLink>
            </p>
          ) : (
            <p className="text-center text-small">
              Already have an account?&nbsp;
              <CustomLink size="base" href="/sign-in" target="_self">
                Log in
              </CustomLink>
            </p>
          )}
        </div>
      </div>
    </div>
  );
};
